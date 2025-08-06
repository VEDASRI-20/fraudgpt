import pandas as pd
df = pd.read_csv("fraud_scores.csv")
print("Fraudulent Transactions (is_fraud=1):")
print(df[df['is_fraud'] == 1][['amount', 'hour_of_day', 'velocity', 'geo_distance', 'fraud_score']].describe())
print("\nNon-Fraudulent Transactions (is_fraud=0):")
print(df[df['is_fraud'] == 0][['amount', 'hour_of_day', 'velocity', 'geo_distance', 'fraud_score']].describe())