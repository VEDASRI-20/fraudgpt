import asyncio
import websockets
import json
import time

async def listen():
    uri = "ws://127.0.0.1:8000/ws/all"
    connection_attempts = 0
    max_attempts = 5
    reconnect_interval = 5

    while connection_attempts < max_attempts:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ Connected to WebSocket at {time.strftime('%H:%M:%S', time.localtime())}")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get('type') == 'pong':
                        print(f"🏓 Received pong at {time.strftime('%H:%M:%S', time.localtime())}")
                        continue
                    print("\n📡 New Transaction:")
                    print(f"  🕒 Timestamp: {data['timestamp']}")
                    print(f"  💰 Amount: ${data['transaction']['amount']:.2f}")
                    print(f"  🎯 Fraud Score: {data['fraud_score']*100:.1f}% ({data['severity']})")
                    print(f"  🚩 Flagged: {'YES' if data['is_flagged'] else 'NO'}")
                    print(f"  📍 Location: {data.get('location', 'Unknown')}")
                    print(f"  📝 Reason: {data['reason']}")
                    if "risk_tags" in data:
                        print(f"  🔖 Risk Tags: {' '.join(data['risk_tags'])}")
        except websockets.exceptions.ConnectionClosed:
            print(f"⚠ Connection closed, attempting reconnect ({connection_attempts + 1}/{max_attempts})...")
            connection_attempts += 1
            await asyncio.sleep(reconnect_interval)
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    print("❌ Max reconnection attempts reached. Please check the backend.")

if __name__ == "__main__":
    asyncio.run(listen())