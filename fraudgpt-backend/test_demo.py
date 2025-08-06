import joblib
import pandas as pd
model_dict = joblib.load("model.joblib")
model = model_dict['model']
scaler = model_dict['scaler']
new_txn = pd.DataFrame([[10000, 2, 6.0, 1200]], columns=['amount', 'hour_of_day', 'velocity', 'geo_distance'])
new_txn_scaled = scaler.transform(new_txn)
score = model.predict_proba(new_txn_scaled)[:, 1]
print(f"Fraud Score: {score[0]:.2f}")