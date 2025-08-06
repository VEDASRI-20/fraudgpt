import pandas as pd
from sklearn.metrics import precision_score, recall_score
df = pd.read_csv(r"C:\Users\VIVEK SHOWRY\Downloads\hackathon\fraud_scores.csv")
y_true = df['is_fraud']
for threshold in [0.3, 0.5, 0.7]:
    y_pred = df['fraud_score'] > threshold
    print(f"\nThreshold: {threshold}")
    print(f"Precision: {precision_score(y_true, y_pred):.2f}")
    print(f"Recall: {recall_score(y_true, y_pred):.2f}")