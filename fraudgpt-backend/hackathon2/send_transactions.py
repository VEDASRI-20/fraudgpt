import pandas as pd
import requests
import time
import argparse
from datetime import datetime
from faker import Faker
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# CLI arguments
parser = argparse.ArgumentParser(description="Simulate real-time transactions with enhanced fraud explanations.")
parser.add_argument("--speed", type=float, default=1.5, help="Delay (seconds) between transactions.")
parser.add_argument("--loop", action="store_true", help="Loop transactions indefinitely.")
parser.add_argument("--detailed", action="store_true", help="Show detailed fraud analysis for flagged transactions.")
parser.add_argument("--save-log", type=str, help="Save detailed logs to specified file.")
args = parser.parse_args()

# Backend API URL (ensure it matches the backend host)
API_URL = "http://127.0.0.1:8000/score"

# Load fraud_scores.csv
try:
    df = pd.read_csv("fraud_scores.csv")
    print(f"✅ Loaded {len(df)} transactions from fraud_scores.csv")
except FileNotFoundError:
    print("❌ fraud_scores.csv not found. Please ensure the file exists.")
    exit(1)
except Exception as e:
    print(f"❌ Error loading fraud_scores.csv: {e}")
    exit(1)

faker = Faker()

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

def print_transaction_summary(txn, result):
    """Print a concise transaction summary."""
    severity_color = get_color_for_severity(result.get('severity', 'UNKNOWN'))
    risk_emoji = get_risk_emoji(result.get('risk_level', result.get('severity', 'UNKNOWN')))
    print(f"\n{'-'*80}")
    print(f"{Fore.CYAN}[{result.get('timestamp', datetime.now().isoformat())}]{Style.RESET_ALL}")
    print(f"💰 Amount: ${txn['amount']:,.2f} | ⏰ Time: {txn['hour_of_day']}:00 | 🏃 Velocity: {txn['velocity']} | 🌍 Distance: {txn['geo_distance']}km")
    print(f"{risk_emoji} {severity_color}Fraud Score: {result.get('fraud_score', 0)*100:.1f}% ({result.get('severity', 'N/A')}) {Style.RESET_ALL} | Flagged: {'YES' if result.get('is_flagged', False) else 'NO'}")
    print(f"📝 {result.get('reason', 'No reason')}")

def print_detailed_analysis(result):
    """Print detailed fraud analysis for flagged transactions."""
    if not result.get('is_flagged', False):
        return
        
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"🔍 DETAILED FRAUD ANALYSIS")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    print(f"\n📊 {Fore.CYAN}Risk Assessment:{Style.RESET_ALL}")
    print(f"   • Overall Risk Level: {get_risk_emoji(result.get('risk_level', 'UNKNOWN'))} {result.get('risk_level', 'UNKNOWN')}")
    print(f"   • Confidence Score: {result.get('confidence', 'N/A')}")
    print(f"   • Factors Analyzed: {result.get('factors_analyzed', 0)}")
    
    print(f"\n🎯 {Fore.CYAN}Primary Risk Factor:{Style.RESET_ALL}")
    print(f"   • {result.get('primary_reason', 'N/A')}")
    
    print(f"\n📋 {Fore.CYAN}Detailed Analysis:{Style.RESET_ALL}")
    print(f"   • {result.get('detailed_explanation', 'No details')}")
    
    print(f"\n🎯 {Fore.CYAN}Recommendation:{Style.RESET_ALL}")
    print(f"   • {result.get('recommendation', 'N/A')}")
    
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

def log_transaction(txn, result, log_file):
    """Log transaction details to file."""
    if not log_file:
        return
        
    try:
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*100}\n")
            f.write(f"Timestamp: {result.get('timestamp', datetime.now().isoformat())}\n")
            f.write(f"Transaction: Amount=${txn['amount']}, Hour={txn['hour_of_day']}, Velocity={txn['velocity']}, Distance={txn['geo_distance']}km\n")
            f.write(f"Result: Score={result.get('fraud_score', 0)}, Severity={result.get('severity', 'N/A')}, Flagged={result.get('is_flagged', False)}\n")
            f.write(f"Reason: {result.get('reason', 'No reason')}\n")
            if result.get('is_flagged', False):
                f.write(f"Risk Level: {result.get('risk_level', 'N/A')}\n")
                f.write(f"Primary Reason: {result.get('primary_reason', 'N/A')}\n")
                f.write(f"Detailed Analysis: {result.get('detailed_explanation', 'No details')}\n")
                f.write(f"Recommendation: {result.get('recommendation', 'N/A')}\n")
    except Exception as e:
        print(f"❌ Error writing to log file: {e}")

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
            for idx, row in df.iterrows():
                transaction_count += 1
                
                # Prepare transaction data
                txn = {
                    "amount": float(row["amount"]),
                    "hour_of_day": int(row["hour_of_day"]),
                    "velocity": float(row["velocity"]),
                    "geo_distance": float(row["geo_distance"])
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
                            print(f"❌ Retry {attempt + 1}/3 for transaction {idx}: {e}")
                            time.sleep(2 ** attempt)
                    
                    result = response.json()
                    if result.get('error'):
                        print(f"❌ API Error: {result['error']}")
                        continue
                    
                    # Count fraud cases
                    if result.get('is_flagged', False):
                        fraud_count += 1
                    
                    # Print transaction summary
                    print_transaction_summary(txn, result)
                    
                    # Print detailed analysis if requested and transaction is flagged
                    if args.detailed and result.get('is_flagged', False):
                        print_detailed_analysis(result)
                    
                    # Log transaction
                    log_transaction(txn, result, args.save_log)
                    
                except requests.exceptions.RequestException as e:
                    print(f"❌ Connection error for transaction {idx}: {e}")
                except Exception as e:
                    print(f"❌ Unexpected error for transaction {idx}: {e}")
                
                # Wait before next transaction
                time.sleep(args.speed)
            
            # Print summary statistics
            fraud_rate = (fraud_count / transaction_count) * 100 if transaction_count > 0 else 0
            print(f"\n{Fore.CYAN}📊 Session Statistics:{Style.RESET_ALL}")
            print(f"   • Total Transactions: {transaction_count}")
            print(f"   • Fraud Cases: {fraud_count}")
            print(f"   • Fraud Rate: {fraud_rate:.1f}%")
            
            if not args.loop:
                break
                
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}🛑 Simulation stopped by user{Style.RESET_ALL}")
        fraud_rate = (fraud_count / transaction_count) * 100 if transaction_count > 0 else 0
        print(f"\n{Fore.CYAN}📊 Final Statistics:{Style.RESET_ALL}")
        print(f"   • Total Transactions Processed: {transaction_count}")
        print(f"   • Fraud Cases Detected: {fraud_count}")
        print(f"   • Overall Fraud Rate: {fraud_rate:.1f}%")
        
        if args.save_log:
            print(f"   • Detailed logs saved to: {args.save_log}")

if __name__ == "__main__":
    try:
        import colorama
    except ImportError:
        print("Installing colorama for colored output...")
        import subprocess
        subprocess.check_call(["pip", "install", "colorama"])
        import colorama
    
    main()