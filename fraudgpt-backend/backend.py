import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pytz import timezone
import uvicorn
import joblib
import numpy as np
from catboost import CatBoostClassifier  # Use the correct model class
from sklearn.preprocessing import StandardScaler
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s IST - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
ist = timezone('Asia/Kolkata')

# Initialize FastAPI application
app = FastAPI(title="Fraud Detection API with ML Model")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration
FRAUD_THRESHOLD = 0.5
MODEL_FILE = 'model.joblib'

# WebSocket connection pools
all_connections: List[WebSocket] = []
fraud_only_connections: List[WebSocket] = []
analysis_connections: List[WebSocket] = []

# Global store for analysis data
analysis_data = {
    "hourly_fraud": {i: 0 for i in range(24)},  # Fraud counts by hour
    "severity_counts": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}  # Fraud counts by severity
}

# Data Models
class Transaction(BaseModel):
    amount: float
    hour_of_day: int
    velocity: float
    geo_distance: float

class TransactionPayload(BaseModel):
    id: int
    timestamp: str
    fraud_score: float
    is_flagged: bool
    severity: str
    reason: str
    detailed_explanation: str
    risk_level: str
    primary_reason: str
    recommendation: str
    confidence: str
    factors_analyzed: Dict[str, Any]
    transaction: Dict[str, Any]

# In-memory store for transaction history (optional, not currently used)
transaction_history = []

# Load the trained model and scaler at startup
model = None
scaler = None
try:
    loaded_data = joblib.load(MODEL_FILE)
    model = loaded_data.get('model')
    scaler = loaded_data.get('scaler')

    if model is None or scaler is None:
        logger.error(f"❌ Model file '{MODEL_FILE}' is missing model or scaler objects. Please re-run the training script.")
    else:
        logger.info("✅ Successfully loaded machine learning model and scaler.")
        if not hasattr(model, 'feature_names_'):
            logger.warning("Model does not have feature_names_. Assuming feature order: ['amount', 'hour_of_day', 'velocity', 'geo_distance']")
except FileNotFoundError:
    logger.error(f"❌ Model file '{MODEL_FILE}' not found. Please ensure the model exists.")
except Exception as e:
    logger.error(f"❌ Error loading model: {e}")

# Fraud Explainer Class (remains rule-based for explanations)
class FraudExplainer:
    def __init__(self):
        self.risk_thresholds = {
            'amount': {'low': 500, 'medium': 1500, 'high': 3000, 'extreme': 7000},
            'velocity': {'low': 2, 'medium': 4, 'high': 7, 'extreme': 12},
            'geo_distance': {'low': 50, 'medium': 150, 'high': 500, 'extreme': 1000},
            'hour_risk': {
                'safe': list(range(9, 18)), 'moderate': [8, 18, 19, 20],
                'risky': [21, 22, 23, 6, 7], 'dangerous': [0, 1, 2, 3, 4, 5]
            }
        }
    def analyze_risk_factors(self, txn: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        factors: Dict[str, Dict[str, Any]] = {}
        amt = txn.get('amount', 0)
        if amt >= self.risk_thresholds['amount']['extreme']:
            factors['amount'] = {'level': 'EXTREME', 'score': 4, 'description': f'Extremely high amount (${amt:,.2f})', 'context': 'Amounts over $7,000 are high fraud risk'}
        elif amt >= self.risk_thresholds['amount']['high']:
            factors['amount'] = {'level': 'HIGH', 'score': 3, 'description': f'Large transaction (${amt:,.2f})', 'context': 'Large amounts may indicate fraud'}
        elif amt >= self.risk_thresholds['amount']['medium']:
            factors['amount'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Elevated amount (${amt:,.2f})', 'context': 'Above-average amounts require review'}
        elif amt >= self.risk_thresholds['amount']['low']:
            factors['amount'] = {'level': 'LOW', 'score': 1, 'description': f'Moderately high amount (${amt:,.2f})', 'context': 'Slightly elevated amount'}

        hr = txn.get('hour_of_day', -1)
        if hr in self.risk_thresholds['hour_risk']['dangerous']:
            factors['timing'] = {'level': 'EXTREME', 'score': 4, 'description': f'Transaction at {hr}:00', 'context': 'Midnight–6AM has very high fraud rates'}
        elif hr in self.risk_thresholds['hour_risk']['risky']:
            factors['timing'] = {'level': 'HIGH', 'score': 3, 'description': f'Late evening at {hr}:00', 'context': 'Evening transactions often flagged'}
        elif hr in self.risk_thresholds['hour_risk']['moderate']:
            factors['timing'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Off-business hours at {hr}:00', 'context': 'Outside 9–5 needs scrutiny'}

        vel = txn.get('velocity', 0)
        if vel >= self.risk_thresholds['velocity']['extreme']:
            factors['velocity'] = {'level': 'EXTREME', 'score': 4, 'description': f'Very high frequency ({int(vel)} txns)', 'context': 'Automated/bot activity likely'}
        elif vel >= self.risk_thresholds['velocity']['high']:
            factors['velocity'] = {'level': 'HIGH', 'score': 3, 'description': f'High frequency ({int(vel)} txns)', 'context': 'Clustering suggests fraud'}
        elif vel >= self.risk_thresholds['velocity']['medium']:
            factors['velocity'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Elevated frequency ({int(vel)} txns)', 'context': 'Above normal pace'}
        elif vel >= self.risk_thresholds['velocity']['low']:
            factors['velocity'] = {'level': 'LOW', 'score': 1, 'description': f'Moderate frequency ({int(vel)} txns)', 'context': 'Slightly elevated'}

        dist = txn.get('geo_distance', 0)
        if dist >= self.risk_thresholds['geo_distance']['extreme']:
            factors['geography'] = {'level': 'EXTREME', 'score': 4, 'description': f'Cross-country ({dist:.0f}km)', 'context': 'Stolen credentials likely'}
        elif dist >= self.risk_thresholds['geo_distance']['high']:
            factors['geography'] = {'level': 'HIGH', 'score': 3, 'description': f'Long distance ({dist:.0f}km)', 'context': 'Location anomaly'}
        elif dist >= self.risk_thresholds['geo_distance']['medium']:
            factors['geography'] = {'level': 'MEDIUM', 'score': 2, 'description': f'Unusual distance ({dist:.0f}km)', 'context': 'Outside typical range'}
        elif dist >= self.risk_thresholds['geo_distance']['low']:
            factors['geography'] = {'level': 'LOW', 'score': 1, 'description': f'Slight distance ({dist:.0f}km)', 'context': 'Slightly outside normal'}
        return factors

    def generate_comprehensive_explanation(self, txn: Dict[str, Any], score: float, is_flagged: bool) -> Dict[str, Any]:
        factors = self.analyze_risk_factors(txn)
        if not is_flagged:
            return {
                'explanation': 'Transaction appears legitimate.', 'risk_level': 'LOW',
                'detailed_analysis': 'All parameters within normal ranges.',
                'recommendation': 'Approve with standard monitoring.',
                'confidence': f'{(1-score)*100:.1f}%', 'factors_analyzed': {}
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
            'risk_level': risk, 'detailed_analysis': detailed,
            'primary_reason': factors[primary]['description'] if primary else None,
            'recommendation': action, 'confidence': f'{score*100:.1f}%',
            'factors_analyzed': factors
        }

explainer = FraudExplainer()

# Helper function to get model prediction
def predict_fraud_score(txn_data: Dict[str, Any]) -> float:
    if model is None or scaler is None:
        logger.error("Model or scaler not loaded. Cannot predict.")
        return 0.0

    try:
        features = np.array([
            txn_data['amount'],
            txn_data['hour_of_day'],
            txn_data['velocity'],
            txn_data['geo_distance']
        ]).reshape(1, -1)
        
        # Scale the features before prediction!
        scaled_features = scaler.transform(features)

        # Predict the probability of the transaction being fraudulent
        fraud_prob = model.predict_proba(scaled_features)[:, 1]
        return float(fraud_prob)

    except KeyError as e:
        logger.error(f"❌ Missing data key in transaction payload: {e}")
        return 0.0

    except Exception as e:
        logger.error(f"❌ Error during model prediction: {e}")
        return 0.0

# Broadcast helpers
async def broadcast_all(msg: Dict[str, Any]):
    for conn in all_connections[:]:
        try:
            await conn.send_json(msg)
        except Exception:
            all_connections.remove(conn)

async def broadcast_fraud(msg: Dict[str, Any]):
    for conn in fraud_only_connections[:]:
        try:
            await conn.send_json(msg)
        except Exception:
            fraud_only_connections.remove(conn)

async def broadcast_analysis():
    while True:
        await asyncio.sleep(5)  # Broadcast every 5 seconds
        for conn in analysis_connections[:]:
            try:
                await conn.send_json({
                    "type": "analysis_update",
                    "hourly_fraud": analysis_data["hourly_fraud"],
                    "severity_counts": analysis_data["severity_counts"],
                    "timestamp": ist.localize(datetime.utcnow()).isoformat()
                })
            except Exception:
                analysis_connections.remove(conn)

# WebSocket endpoints
@app.websocket("/ws/all")
async def websocket_all(ws: WebSocket):
    await ws.accept()
    all_connections.append(ws)
    logger.info(f"New WebSocket connection established for all alerts from IP {ws.client.host}")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        all_connections.remove(ws)
        logger.info(f"WebSocket connection closed for all alerts from IP {ws.client.host}")
    except Exception as e:
        logger.error(f"WebSocket error for IP {ws.client.host}: {e}")
        all_connections.remove(ws)

@app.websocket("/ws/fraud-only")
async def websocket_fraud(ws: WebSocket):
    await ws.accept()
    fraud_only_connections.append(ws)
    logger.info(f"New WebSocket connection established for fraud-only alerts from IP {ws.client.host}")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        fraud_only_connections.remove(ws)
        logger.info(f"WebSocket connection closed for fraud-only alerts from IP {ws.client.host}")
    except Exception as e:
        logger.error(f"WebSocket error for IP {ws.client.host}: {e}")
        fraud_only_connections.remove(ws)

@app.websocket("/ws/analysis")
async def websocket_analysis(ws: WebSocket):
    await ws.accept()
    analysis_connections.append(ws)
    logger.info(f"New WebSocket connection established for analysis from IP {ws.client.host}")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        analysis_connections.remove(ws)
        logger.info(f"WebSocket connection closed for analysis from IP {ws.client.host}")
    except Exception as e:
        logger.error(f"WebSocket error for analysis from IP {ws.client.host}: {e}")
        analysis_connections.remove(ws)

# New API endpoint to receive transactions from send_transactions.py
@app.post("/score")
async def score_transaction(txn: Transaction = Body(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Machine learning model not loaded.")
        
    # Convert incoming transaction to a dictionary
    txn_dict = txn.dict()
    
    # Use the model to predict the fraud score
    fraud_score = predict_fraud_score(txn_dict)
    is_flagged = fraud_score > FRAUD_THRESHOLD
    
    if fraud_score >= 0.8: severity = "CRITICAL"
    elif fraud_score >= 0.6: severity = "HIGH"
    elif fraud_score >= 0.4: severity = "MEDIUM"
    else: severity = "LOW"
    
    details = explainer.generate_comprehensive_explanation(txn_dict, fraud_score, is_flagged)
    
    # Update analysis data
    hour = txn_dict.get("hour_of_day", 0)
    if hour in analysis_data["hourly_fraud"]:
        analysis_data["hourly_fraud"][hour] += 1
    if severity in analysis_data["severity_counts"]:
        analysis_data["severity_counts"][severity] += 1
    
    # Create the payload for the dashboard
    payload = TransactionPayload(
        id=random.randint(100000, 999999),
        timestamp=ist.localize(datetime.utcnow()).isoformat(),
        fraud_score=round(fraud_score, 3),
        is_flagged=is_flagged,
        severity=severity,
        reason=details['explanation'],
        detailed_explanation=details.get('detailed_analysis', ''),
        risk_level=details.get('risk_level', 'LOW'),
        primary_reason=details.get('primary_reason', ''),
        recommendation=details.get('recommendation', 'Standard monitoring.'),
        confidence=details.get('confidence', '100.0%'),
        factors_analyzed=details.get('factors_analyzed', {}),
        transaction=txn_dict
    )
    
    # Broadcast the result to the connected clients
    await broadcast_all(payload.dict())
    if payload.is_flagged:
        await broadcast_fraud(payload.dict())
    
    logger.info(f"Received and scored transaction. Score: {payload.fraud_score}")
    
    # The endpoint returns a response, but the dashboard primarily listens to the WebSocket
    return {"message": "Transaction scored and broadcasted", "fraud_score": payload.fraud_score}

if __name__ == "__main__":
    # Start the analysis broadcast task
    asyncio.create_task(broadcast_analysis())
    uvicorn.run(app, host="127.0.0.1", port=8080, reload=True)