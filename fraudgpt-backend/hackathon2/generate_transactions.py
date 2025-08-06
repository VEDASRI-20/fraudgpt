import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
n_transactions = 10000
fraud_ratio = 0.15
output_path = "transactions.csv"

data = []
user_ids = [fake.uuid4() for _ in range(1000)]
for i in range(n_transactions):
    user_id = random.choice(user_ids)
    is_fraud = random.random() < fraud_ratio
    timestamp = fake.date_time_between(start_date="-30d", end_date="now")
    if is_fraud:
        if random.random() < 0.7:
            location = random.choice(["New York, NY", "London, UK", "Tokyo, JP"])
        else:
            location = fake.city() + ", " + fake.state_abbr()
        amount = random.uniform(600, 6000) if random.random() < 0.8 else random.uniform(50, 600)
        if random.random() < 0.75:
            timestamp = timestamp.replace(hour=random.randint(0, 4), minute=random.randint(0, 59))
    else:
        location = fake.city() + ", " + fake.state_abbr()
        amount = random.uniform(5, 1200)
    data.append({
        "txn_id": i,
        "user_id": user_id,
        "name": fake.name(),
        "card_number": fake.credit_card_number(),
        "merchant": fake.company(),
        "timestamp": timestamp,
        "location": location,
        "device_id": fake.uuid4(),
        "amount": round(amount, 2),
        "is_fraud": int(is_fraud)
    })

# Add velocity for 25% of frauds
df = pd.DataFrame(data)
fraud_indices = df[df['is_fraud'] == 1].index
for idx in fraud_indices[:len(fraud_indices)//4]:
    user_id = df.at[idx, 'user_id']
    base_time = df.at[idx, 'timestamp']
    for j in range(random.randint(1, 2)):
        df = pd.concat([df, pd.DataFrame([{
            "txn_id": len(df) + j,
            "user_id": user_id,
            "name": df.at[idx, 'name'],
            "card_number": df.at[idx, 'card_number'],
            "merchant": fake.company(),
            "timestamp": base_time + timedelta(minutes=j+1),
            "location": random.choice([df.at[idx, 'location'], random.choice(["New York, NY", "London, UK", "Tokyo, JP"])]),
            "device_id": df.at[idx, 'device_id'],
            "amount": round(random.uniform(600, 6000), 2),
            "is_fraud": 1
        }])], ignore_index=True)

df.to_csv(output_path, index=False)
print(f"Transactions saved to {output_path}")