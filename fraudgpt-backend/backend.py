from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import traceback
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from geopy.geocoders import Nominatim
import logging
from firewall import Firewall
from pytz import timezone
import pandas as pd

# Configure logging with IST
logging.basicConfig(level=logging.INFO, format='%(asctime)s IST - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
ist = timezone('Asia/Kolkata')

# Initialize FastAPI application
app = FastAPI(title="Enhanced Fraud Detection API")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firewall with error handling
try:
    firewall = Firewall(config_path="firewall_config.json")
except Exception as e:
    logger.error(f"Failed to initialize Firewall: {e}")
    firewall = None  # Fallback to allow app to run

# Global fraud threshold configuration
FRAUD_THRESHOLD = 0.5

# WebSocket connection pools
all_connections: List[WebSocket] = []
fraud_only_connections: List[WebSocket] = []

# Data Model for transactions
class Transaction(BaseModel):
    amount: float
    hour_of_day: int
    velocity: float
    geo_distance: float
    latitude: float = None
    longitude: float = None

# Firewall Middleware
@app.middleware("http")
async def firewall_middleware(request: Request, call_next):
    client_ip = request.headers.get('X-Forwarded-For', request.client.host)
    try:
        if firewall and not firewall.is_allowed_ip(client_ip):
            logger.warning(f"Blocked request from IP {client_ip}: IP is blacklisted")
            raise HTTPException(status_code=403, detail="Access denied: IP is blacklisted")
        
        if firewall and not firewall.check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")
        
        if firewall:
            firewall.log_request(client_ip, "ALLOWED")
        response = await call_next(request)
        return response
    except Exception as e:
        if firewall:
            firewall.log_request(client_ip, f"BLOCKED: {str(e)}")
        raise

# Fraud Explainer Class
class FraudExplainer:
    def __init__(self):
        self.risk_thresholds = {
            'amount': {'low': 500, 'medium': 1500, 'high': 3000, 'extreme': 7000},
            'velocity': {'low': 2, 'medium': 4, 'high': 7, 'extreme': 12},
            'geo_distance': {'low': 50, 'medium': 150, 'high': 500, 'extreme': 1000},
            'hour_risk': {
                'safe': list(range(9, 18)),
                'moderate': [8, 18, 19, 20],
                'risky': [21, 22, 23, 6, 7],
                'dangerous': [0, 1, 2, 3, 4, 5]
            }
        }

    def analyze_risk_factors(self, txn: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        factors: Dict[str, Dict[str, Any]] = {}
        amt = txn['amount']
        if amt >= self.risk_thresholds['amount']['extreme']:
            factors['amount'] = {'level': 'EXTREME', 'score': 4, 'description': f'Extremely high amount (${amt:,.2f})', 'context': 'Amounts over $7,000 are high fraud risk'}
        elif amt >= self.risk_thresholds['amount']['high']:
            factors['amount'] = {'level': 'HIGH', 'score': 3, 'description': f'Large transaction (${amt:,.2f})', 'context': 'Large amounts may indicate fraud'}
        elif amt >= self.risk_thresholds['amount']['medium']:
            factors['amount'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Elevated amount (${amt:,.2f})', 'context': 'Above-average amounts require review'}
        elif amt >= self.risk_thresholds['amount']['low']:
            factors['amount'] = {'level': 'LOW', 'score': 1, 'description': f'Moderately high amount (${amt:,.2f})', 'context': 'Slightly elevated amount'}
        hr = txn['hour_of_day']
        if hr in self.risk_thresholds['hour_risk']['dangerous']:
            factors['timing'] = {'level': 'EXTREME', 'score': 4, 'description': f'Transaction at {hr}:00', 'context': 'Midnight–6AM has very high fraud rates'}
        elif hr in self.risk_thresholds['hour_risk']['risky']:
            factors['timing'] = {'level': 'HIGH', 'score': 3, 'description': f'Late evening at {hr}:00', 'context': 'Evening transactions often flagged'}
        elif hr in self.risk_thresholds['hour_risk']['moderate']:
            factors['timing'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Off-business hours at {hr}:00', 'context': 'Outside 9–5 needs scrutiny'}
        vel = txn['velocity']
        if vel >= self.risk_thresholds['velocity']['extreme']:
            factors['velocity'] = {'level': 'EXTREME', 'score': 4, 'description': f'Very high frequency ({int(vel)} txns)', 'context': 'Automated/bot activity likely'}
        elif vel >= self.risk_thresholds['velocity']['high']:
            factors['velocity'] = {'level': 'HIGH', 'score': 3, 'description': f'High frequency ({int(vel)} txns)', 'context': 'Clustering suggests fraud'}
        elif vel >= self.risk_thresholds['velocity']['medium']:
            factors['velocity'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Elevated frequency ({int(vel)} txns)', 'context': 'Above normal pace'}
        elif vel >= self.risk_thresholds['velocity']['low']:
            factors['velocity'] = {'level': 'LOW', 'score': 1, 'description': f'Moderate frequency ({int(vel)} txns)', 'context': 'Slightly elevated'}
        dist = txn['geo_distance']
        if dist >= self.risk_thresholds['geo_distance']['extreme']:
            factors['geography'] = {'level': 'EXTREME', 'score': 4, 'description': f'Cross-country ({dist:.0f}km)', 'context': 'Stolen credentials likely'}
        elif dist >= self.risk_thresholds['geo_distance']['high']:
            factors['geography'] = {'level': 'HIGH', 'score': 3, 'description': f'Long distance ({dist:.0f}km)', 'context': 'Location anomaly'}
        elif dist >= self.risk_thresholds['geo_distance']['medium']:
            factors['geography'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Unusual distance ({dist:.0f}km)', 'context': 'Outside typical range'}
        elif dist >= self.risk_thresholds['geo_distance']['low']:
            factors['geography'] = {'level': 'LOW', 'score': 1, 'description': f'Moderate distance ({dist:.0f}km)', 'context': 'Slightly outside normal'}
        return factors

    def generate_comprehensive_explanation(self, txn: Dict[str, Any], score: float, is_flagged: bool) -> Dict[str, Any]:
        factors = self.analyze_risk_factors(txn)
        if not is_flagged:
            return {
                'explanation': 'Transaction appears legitimate.',
                'risk_level': 'LOW',
                'detailed_analysis': 'All parameters within normal ranges.',
                'recommendation': 'Approve with standard monitoring.',
                'confidence': f'{(1-score)*100:.1f}%'
            }
        total_score = sum(f['score'] for f in factors.values())
        primary = max(factors.items(), key=lambda x: x[1]['score'])[0] if factors else None
        explanations = [f['description'] for f in factors.values()]
        detailed = " & ".join(explanations)
        if total_score >= 12:
            risk = 'CRITICAL'; action = 'BLOCK IMMEDIATELY'
        elif total_score >= 9:
            risk = 'HIGH'; action = 'MANUAL REVIEW REQUIRED'
        elif total_score >= 6:
            risk = 'MEDIUM'; action = 'ENHANCED MONITORING'
        else:
            risk = 'LOW-MEDIUM'; action = 'STANDARD MONITORING'
        return {
            'explanation': explanations[0] if len(explanations) == 1 else detailed,
            'risk_level': risk,
            'detailed_analysis': detailed,
            'primary_reason': factors[primary]['description'] if primary else None,
            'recommendation': action,
            'confidence': f'{score*100:.1f}%'
        }

explainer = FraudExplainer()

# Simple scoring function
def calculate_fraud_score(txn: Dict[str, Any]) -> float:
    score = 0.0
    amt, hr, vel, dist = txn['amount'], txn['hour_of_day'], txn['velocity'], txn['geo_distance']
    if amt > 5000: score += 0.4
    elif amt > 2000: score += 0.25
    elif amt > 1000: score += 0.15
    if hr in range(0, 6): score += 0.3
    elif hr in range(21, 24): score += 0.2
    if vel > 10: score += 0.35
    elif vel > 5: score += 0.2
    elif vel > 2: score += 0.1
    if dist > 1000: score += 0.3
    elif dist > 500: score += 0.2
    elif dist > 100: score += 0.1
    return min(score, 1.0)

# WebSocket endpoint for all connections with ping-pong
@app.websocket("/ws/all")
async def websocket_all(ws: WebSocket):
    client_ip = ws.headers.get('X-Forwarded-For', ws.client.host)
    if firewall and not firewall.is_allowed_ip(client_ip):
        logger.warning(f"Blocked WebSocket connection from IP {client_ip}: IP is blacklisted")
        await ws.close(code=1008, reason="Access denied: IP is blacklisted")
        if firewall:
            firewall.log_request(client_ip, "BLOCKED: WebSocket IP blacklisted")
        return
    await ws.accept()
    all_connections.append(ws)
    logger.info(f"New WebSocket connection established for all alerts from IP {client_ip}")
    if firewall:
        firewall.log_request(client_ip, "ALLOWED: WebSocket /ws/all connected")
    try:
        while True:
            data = await ws.receive_text()
            if data == '{"type": "ping"}':
                await ws.send_text(json.dumps({"type": "pong"}))
            else:
                fraud_message = {
                    "timestamp": ist.localize(datetime.utcnow()).isoformat(),
                    "transaction": {"amount": 245.67},
                    "fraud_score": 0.82,
                    "severity": "High",
                    "is_flagged": True,
                    "location": "New York, USA",
                    "reason": "Unusual location & high amount",
                    "risk_tags": ["geo-risk", "velocity"]
                }
                await broadcast_all(fraud_message)
                if fraud_message["is_flagged"]:
                    await broadcast_fraud(fraud_message)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        all_connections.remove(ws)
        logger.info(f"WebSocket connection closed for all alerts from IP {client_ip}")
        if firewall:
            firewall.log_request(client_ip, "DISCONNECTED: WebSocket /ws/all")
    except Exception as e:
        logger.error(f"WebSocket error for IP {client_ip}: {e}")
        if firewall:
            firewall.log_request(client_ip, f"ERROR: WebSocket /ws/all - {str(e)}")

# WebSocket endpoint for fraud-only connections with ping-pong
@app.websocket("/ws/fraud-only")
async def websocket_fraud(ws: WebSocket):
    client_ip = ws.headers.get('X-Forwarded-For', ws.client.host)
    if firewall and not firewall.is_allowed_ip(client_ip):
        logger.warning(f"Blocked WebSocket connection from IP {client_ip}: IP is blacklisted")
        await ws.close(code=1008, reason="Access denied: IP is blacklisted")
        if firewall:
            firewall.log_request(client_ip, "BLOCKED: WebSocket IP blacklisted")
        return
    await ws.accept()
    fraud_only_connections.append(ws)
    logger.info(f"New WebSocket connection established for fraud-only alerts from IP {client_ip}")
    if firewall:
        firewall.log_request(client_ip, "ALLOWED: WebSocket /ws/fraud-only connected")
    try:
        while True:
            data = await ws.receive_text()
            if data == '{"type": "ping"}':
                await ws.send_text(json.dumps({"type": "pong"}))
            else:
                fraud_message = {
                    "timestamp": ist.localize(datetime.utcnow()).isoformat(),
                    "transaction": {"amount": 987.45},
                    "fraud_score": 0.95,
                    "severity": "Critical",
                    "is_flagged": True,
                    "location": "London, UK",
                    "reason": "Multiple failed attempts",
                    "risk_tags": ["multi-fail", "ip-change"]
                }
                await broadcast_fraud(fraud_message)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        fraud_only_connections.remove(ws)
        logger.info(f"WebSocket connection closed for fraud-only alerts from IP {client_ip}")
        if firewall:
            firewall.log_request(client_ip, "DISCONNECTED: WebSocket /ws/fraud-only")
    except Exception as e:
        logger.error(f"WebSocket error for IP {client_ip}: {e}")
        if firewall:
            firewall.log_request(client_ip, f"ERROR: WebSocket /ws/fraud-only - {str(e)}")

# Broadcast helpers
async def broadcast_all(msg: Dict[str, Any]):
    for conn in all_connections[:]:
        try:
            await conn.send_json(msg)
        except Exception as e:
            logger.error(f"Error broadcasting to connection: {e}")
            all_connections.remove(conn)

async def broadcast_fraud(msg: Dict[str, Any]):
    for conn in fraud_only_connections[:]:
        try:
            await conn.send_json(msg)
        except Exception as e:
            logger.error(f"Error broadcasting to fraud connection: {e}")
            fraud_only_connections.remove(conn)

# Config endpoint to update threshold
@app.post("/config")
def update_config(threshold: float = None):
    global FRAUD_THRESHOLD
    if threshold is not None:
        FRAUD_THRESHOLD = min(max(threshold, 0.0), 1.0)
        logger.info(f"Threshold updated to {FRAUD_THRESHOLD}")
        return {"message": f"Threshold set to {FRAUD_THRESHOLD}"}
    return {"message": "No change"}

# Score endpoint for transaction analysis
@app.post("/score")
async def score_transaction(transaction: Transaction):
    txn = transaction.dict()
    location_name = None
    if txn.get("latitude") and txn.get("longitude"):
        geolocator = Nominatim(user_agent="fraud_detection_app")
        try:
            loc = geolocator.reverse(f"{txn['latitude']},{txn['longitude']}", timeout=5)
            location_name = loc.raw['address'].get('city', loc.raw['address'].get('country', 'Unknown'))
        except Exception as e:
            logger.error(f"Geolocation error: {e}")
            location_name = "Unknown"

    try:
        fraud_score = calculate_fraud_score(txn)
        is_flagged = fraud_score > FRAUD_THRESHOLD

        if fraud_score >= 0.8:
            severity = "CRITICAL"
        elif fraud_score >= 0.6:
            severity = "HIGH"
        elif fraud_score >= 0.4:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        details = explainer.generate_comprehensive_explanation(txn, fraud_score, is_flagged)

        payload = {
            "timestamp": ist.localize(datetime.utcnow()).isoformat(),
            "fraud_score": round(fraud_score, 3),
            "is_flagged": is_flagged,
            "severity": severity,
            "reason": f"{details['explanation']}\n{details.get('primary_reason', '')}",
            "detailed_explanation": details.get("detailed_analysis"),
            "risk_level": details.get("risk_level"),
            "primary_reason": details.get("primary_reason"),
            "recommendation": details.get("recommendation"),
            "confidence": details.get("confidence"),
            "factors_analyzed": details.get("factors_analyzed", 0),
            "location": location_name or "Unknown",
            "transaction": txn
        }

        await broadcast_all(payload)
        if is_flagged:
            await broadcast_fraud(payload)

        logger.info(f"Processed transaction: Score={fraud_score}, Flagged={is_flagged}")
        return payload

    except Exception as e:
        logger.error(f"[ERROR] in /score: {e}")
        traceback.print_exc()
        return {"error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": ist.localize(datetime.utcnow()).isoformat(), "connections": len(all_connections)}

# Statistics endpoint
@app.get("/stats")
async def get_stats():
    firewall_stats = {
        "whitelisted_ips": 0,
        "blacklisted_ips": 0,
        "active_ips": 0,
        "rate_limit_requests": 0,
        "rate_limit_window_seconds": 0
    }
    if firewall:
        firewall_stats = firewall.get_stats()
    return {
        "total_connections": len(all_connections) + len(fraud_only_connections),
        "fraud_threshold": FRAUD_THRESHOLD,
        "last_updated": ist.localize(datetime.utcnow()).isoformat(),
        "firewall_stats": firewall_stats
    }

# Endpoint for flagged transactions
@app.get("/api/flagged-transactions")
async def get_flagged_transactions():
    try:
        df = pd.read_csv('fraud_scores.csv')
        flagged_df = df[df['fraud_score'] > FRAUD_THRESHOLD].copy()
        flagged_df['id'] = range(1, len(flagged_df) + 1)
        flagged_df['timestamp'] = ist.localize(datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')
        if flagged_df.empty:
            return {"message": "No flagged transactions found", "data": []}
        flagged_data = flagged_df[['id', 'amount', 'timestamp', 'fraud_score']].to_dict(orient='records')
        logger.info(f"Retrieved {len(flagged_data)} flagged transactions")
        return flagged_data
    except FileNotFoundError:
        logger.error("fraud_scores.csv not found")
        raise HTTPException(status_code=404, detail="Fraud scores data not found")
    except Exception as e:
        logger.error(f"Error retrieving flagged transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for all transactions
@app.get("/api/all-transactions")
async def get_all_transactions():
    try:
        df = pd.read_csv('fraud_scores.csv')
        df['id'] = range(1, len(df) + 1)
        df['timestamp'] = ist.localize(datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')
        if df.empty:
            return {"message": "No transactions found", "data": []}
        all_data = df[['id', 'amount', 'timestamp', 'fraud_score']].to_dict(orient='records')
        logger.info(f"Retrieved {len(all_data)} transactions")
        return all_data
    except FileNotFoundError:
        logger.error("fraud_scores.csv not found")
        raise HTTPException(status_code=404, detail="Fraud scores data not found")
    except Exception as e:
        logger.error(f"Error retrieving all transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for transaction analysis (flagged counts by hour)
@app.get("/api/transaction-analysis")
async def get_transaction_analysis():
    try:
        df = pd.read_csv('fraud_scores.csv')
        # Group by hour_of_day and count flagged transactions
        analysis_df = df[df['fraud_score'] > FRAUD_THRESHOLD].groupby('hour_of_day').size().reset_index(name='flagged_count')
        if analysis_df.empty:
            return {"message": "No flagged transactions for analysis", "data": []}
        # Map hours to a synthetic date for chart compatibility
        data = {
            "labels": [f"2025-07-30 {h}:00" for h in analysis_df['hour_of_day']],
            "datasets": [{
                "label": "Flagged Frauds per Hour",
                "data": analysis_df['flagged_count'].tolist(),
                "backgroundColor": '#f87171',
                "borderRadius": 6,
            }]
        }
        logger.info(f"Generated analysis for {len(analysis_df)} hours")
        return data
    except FileNotFoundError:
        logger.error("fraud_scores.csv not found")
        raise HTTPException(status_code=404, detail="Fraud scores data not found")
    except Exception as e:
        logger.error(f"Error generating transaction analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Run the application
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Fix for Python 3.13 on Windows
    logger.info("Starting Fraud Detection API with Firewall on http://127.0.0.1:8000")
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)