import pandas as pd
from catboost import CatBoostClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Load features
input_path = "features.csv"
output_model_path = "model.joblib"
output_scores_path = "fraud_scores.csv"
df = pd.read_csv(input_path)

# Features and labels
features = ['amount', 'hour_of_day', 'velocity', 'geo_distance']
X = df[features]
y = df['is_fraud']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=features)

# Train CatBoost
cat = CatBoostClassifier(
    iterations=30,
    depth=2,
    learning_rate=0.05,
    l2_leaf_reg=7.0,
    auto_class_weights='Balanced',
    random_seed=42,
    verbose=0
)
cat.fit(X_scaled, y)

# Predict fraud scores
fraud_scores = cat.predict_proba(X_scaled)[:, 1]

# Save results
df['fraud_score'] = fraud_scores
df.to_csv(output_scores_path, index=False)
print(f"Fraud scores saved to {output_scores_path}")

# Save model and scaler
joblib.dump({'model': cat, 'scaler': scaler}, output_model_path)
print(f"Model and scaler saved to {output_model_path}")