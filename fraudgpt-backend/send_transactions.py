import pandas as pd
import requests
import time
import argparse
import random
from datetime import datetime
from colorama import init, Fore, Style
import geopy.geocoders
import haversine as hs
import sys
import subprocess

# --- Library Check and Installation ---
# This block ensures all required libraries are installed before running.
def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
            __import__(package)
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")
            sys.exit(1)

# Initialize colorama for colored output
init(autoreset=True)

# Install required libraries if they aren't present
install_and_import('colorama')
install_and_import('pandas')
install_and_import('requests')
install_and_import('geopy')
install_and_import('haversine')

# CLI arguments
parser = argparse.ArgumentParser(description="Simulate real-time transactions with enhanced fraud explanations.")
parser.add_argument("--speed", type=float, default=1.5, help="Delay (seconds) between transactions.")
parser.add_argument("--loop", action="store_true", help="Loop transactions indefinitely.")
parser.add_argument("--detailed", action="store_true", help="Show detailed fraud analysis for flagged transactions.")
parser.add_argument("--save-log", type=str, help="Save detailed logs to specified file.")
args = parser.parse_args()

# Backend API URL (ensure it matches the backend host)
API_URL = "http://127.0.0.1:8080/score"

# Load transactions.csv and sort by timestamp to maintain logical history
try:
    df = pd.read_csv("transactions.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')
    print(f"✅ Loaded {len(df)} transactions from transactions.csv")
except FileNotFoundError:
    print("❌ transactions.csv not found. Please ensure the file exists.")
    exit(1)
except Exception as e:
    print(f"❌ Error loading transactions.csv: {e}")
    exit(1)

# In-memory stores for feature engineering
transaction_history = []
location_cache = {}
geolocator = geopy.geocoders.Nominatim(user_agent="fraud_simulation")
VELOCITY_WINDOW_MINUTES = 60

# --- Helper Functions for Feature Engineering ---
def get_coordinates(location_name: str):
    """Fetches and caches geolocation coordinates for a location string."""
    if location_name in location_cache:
        return location_cache[location_name]
    
    try:
        loc = geolocator.geocode(location_name, timeout=5)
        if loc:
            coords = (loc.latitude, loc.longitude)
            location_cache[location_name] = coords
            return coords
    except Exception as e:
        # Geolocation lookup is a best-effort feature.
        # It's okay if it fails, we just log and continue.
        # print(f"⚠️ Geolocation lookup for '{location_name}' failed: {e}")
        pass # Suppress the warning to keep the output cleaner.
    return None

def calculate_geo_distance(current_coords, recent_coords):
    """Calculates haversine distance between two sets of coordinates."""
    if current_coords and recent_coords:
        distance = hs.haversine(current_coords, recent_coords)
        return distance
    return 0.0

def calculate_velocity(user_id, current_timestamp, transaction_history):
    """Calculates transaction velocity for a user within a time window."""
    window_start = current_timestamp - pd.Timedelta(minutes=VELOCITY_WINDOW_MINUTES)
    velocity_count = 0
    # The history list is filtered for the current user and time window
    for tx in transaction_history:
        if tx.get('user_id') == user_id and tx.get('timestamp') > window_start:
            velocity_count += 1
    return velocity_count

# --- Printing and Logging Functions (Unchanged from your code) ---
def get_color_for_severity(severity):
    """Return appropriate color for severity level."""
    colors = {
        'LOW': Fore.GREEN,
        'MEDIUM': Fore.YELLOW,
        'HIGH': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    return colors.get(severity, Fore.WHITE)

def get_risk_emoji(risk_level):
    """Return appropriate emoji for risk level."""
    emojis = {
        'LOW': '✅',
        'MEDIUM': '⚠️',
        'HIGH': '🚨',
        'CRITICAL': '🔥'
    }
    return emojis.get(risk_level, '❓')

def print_transaction_summary(transaction_id, txn, result):
    """Print a concise transaction summary."""
    severity_color = get_color_for_severity(result.get('severity', 'UNKNOWN'))
    risk_emoji = get_risk_emoji(result.get('risk_level', result.get('severity', 'UNKNOWN')))
    print(f"\n{'-'*80}")
    print(f"{Fore.CYAN}[{result.get('timestamp', datetime.now().isoformat())}]{Style.RESET_ALL}")
    print(f"💰 Amount: ${txn['amount']:,.2f} | ⏰ Time: {txn['hour_of_day']}:00 | 🏃 Velocity: {txn['velocity']} | 🌍 Distance: {txn['geo_distance']:.2f}km")
    print(f"❓ {severity_color}Fraud Score: {result.get('fraud_score', 0)*100:.1f}% ({result.get('severity', 'N/A')}) {Style.RESET_ALL} | Flagged: {'YES' if result.get('is_flagged', False) else 'NO'}")
    print(f"📝 {result.get('reason', 'No reason')}")

def print_detailed_analysis(result):
    """Print detailed fraud analysis for flagged transactions."""
    if not result.get('is_flagged', False):
        return
        
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"🔍 DETAILED FRAUD ANALYSIS")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    print(f"\n📊 {Fore.CYAN}Risk Assessment:{Style.RESET_ALL}")
    print(f"  • Overall Risk Level: {get_risk_emoji(result.get('risk_level', 'UNKNOWN'))} {result.get('risk_level', 'UNKNOWN')}")
    print(f"  • Confidence Score: {result.get('confidence', 'N/A')}")
    
    print(f"\n🎯 {Fore.CYAN}Primary Risk Factor:{Style.RESET_ALL}")
    print(f"  • {result.get('primary_reason', 'N/A')}")
    
    print(f"\n📋 {Fore.CYAN}Detailed Analysis:{Style.RESET_ALL}")
    print(f"  • {result.get('detailed_explanation', 'No details')}")
    
    print(f"\n🎯 {Fore.CYAN}Recommendation:{Style.RESET_ALL}")
    print(f"  • {result.get('recommendation', 'N/A')}")
    
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

def log_transaction(transaction_id, txn, result, log_file):
    """Log transaction details to file."""
    if not log_file:
        return
        
    try:
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*100}\n")
            f.write(f"ID: {transaction_id}\n")
            f.write(f"Timestamp: {result.get('timestamp', datetime.now().isoformat())}\n")
            f.write(f"Transaction: Amount=${txn['amount']}, Hour={txn['hour_of_day']}, Velocity={txn['velocity']}, Distance={txn['geo_distance']:.2f}km\n")
            f.write(f"Result: Score={result.get('fraud_score', 0):.2f}, Severity={result.get('severity', 'N/A')}, Flagged={result.get('is_flagged', False)}\n")
            f.write(f"Reason: {result.get('reason', 'No reason')}\n")
            if result.get('is_flagged', False):
                f.write(f"Risk Level: {result.get('risk_level', 'N/A')}\n")
                f.write(f"Primary Reason: {result.get('primary_reason', 'N/A')}\n")
                f.write(f"Detailed Analysis: {result.get('detailed_explanation', 'No details')}\n")
                f.write(f"Recommendation: {result.get('recommendation', 'N/A')}\n")
    except Exception as e:
        print(f"❌ Error writing to log file: {e}")

# --- Main Simulation Loop ---
def main():
    """Main transaction simulation loop."""
    transaction_count = 0
    fraud_count = 0
    
    print(f"🚀 Starting enhanced transaction simulation...")
    print(f"⚙️ Settings: Speed={args.speed}s, Loop={args.loop}, Detailed={args.detailed}")
    if args.save_log:
        print(f"📝 Logging to: {args.save_log}")
        with open(args.save_log, 'w') as f:
            f.write(f"Enhanced Fraud Detection Log - Started at {datetime.now().isoformat()}\n")
    print(f"{'='*80}")
    
    try:
        while True:
            # Randomly select a row index for a more realistic, non-sequential stream
            random_idx = random.randint(0, len(df) - 1)
            row = df.iloc[random_idx]

            transaction_count += 1
            
            # --- Feature Engineering ---
            current_timestamp = row['timestamp']
            hour_of_day = current_timestamp.hour
            
            # Note: Because transactions are now sent randomly, the transaction_history
            # will not be in strict chronological order. This will affect the accuracy of
            # velocity and geo_distance calculations, but it's a trade-off for
            # simulating a random stream of transactions.
            velocity = calculate_velocity(row['user_id'], current_timestamp, transaction_history)
            
            geo_distance = 0
            current_coords = get_coordinates(row['location'])
            if current_coords:
                recent_txn_history = [t for t in transaction_history if t.get('user_id') == row['user_id']]
                if recent_txn_history:
                    last_location = recent_txn_history[-1].get('location')
                    recent_coords = get_coordinates(last_location)
                    if recent_coords:
                        geo_distance = calculate_geo_distance(current_coords, recent_coords)

            # Store the transaction in history for future calculations
            transaction_history.append({
                'user_id': row['user_id'],
                'timestamp': current_timestamp,
                'location': row['location']
            })
            
            # Keep history from getting too large by trimming old entries
            while len(transaction_history) > 1000:
                transaction_history.pop(0)

            # Prepare transaction data for the backend API
            txn = {
                "id": transaction_count, # This is the sequential ID fix
                "amount": float(row["amount"]),
                "hour_of_day": int(hour_of_day),
                "velocity": float(velocity),
                "geo_distance": float(geo_distance)
            }
            
            try:
                # Send transaction to API with retry
                for attempt in range(3):
                    try:
                        response = requests.post(API_URL, json=txn, timeout=10)
                        response.raise_for_status()
                        break
                    except requests.exceptions.RequestException as e:
                        if attempt == 2:
                            raise
                        print(f"❌ Retry {attempt + 1}/3 for transaction {transaction_count}: {e}")
                        time.sleep(2 ** attempt)
                
                result = response.json()
                if result.get('error'):
                    print(f"❌ API Error: {result['error']}")
                    continue
                
                # Count fraud cases
                if result.get('is_flagged', False):
                    fraud_count += 1
                
                # Print transaction summary
                print_transaction_summary(transaction_count, txn, result)
                
                # Print detailed analysis if requested and transaction is flagged
                if args.detailed and result.get('is_flagged', False):
                    print_detailed_analysis(result)
                
                # Log transaction
                log_transaction(transaction_count, txn, result, args.save_log)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error for transaction {transaction_count}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for transaction {transaction_count}: {e}")
            
            # Wait before next transaction
            time.sleep(args.speed)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}🛑 Simulation stopped by user{Style.RESET_ALL}")
    finally:
        fraud_rate = (fraud_count / transaction_count) * 100 if transaction_count > 0 else 0
        print(f"\n{Fore.CYAN}📊 Final Statistics:{Style.RESET_ALL}")
        print(f"  • Total Transactions Processed: {transaction_count}")
        print(f"  • Fraud Cases Detected: {fraud_count}")
        print(f"  • Overall Fraud Rate: {fraud_rate:.1f}%")
        
        if args.save_log:
            print(f"  • Detailed logs saved to: {args.save_log}")

if __name__ == "__main__":
    main()
