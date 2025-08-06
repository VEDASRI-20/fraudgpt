import pandas as pd
import numpy as np
from geopy.distance import geodesic

input_path = "transactions.csv"
output_path = "features.csv"
df = pd.read_csv(input_path)

# Feature engineering
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour_of_day'] = df['timestamp'].dt.hour

# Velocity
df = df.sort_values(['user_id', 'timestamp'])
df['time_diff'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds() / 3600
df['velocity'] = 1 / df['time_diff'].replace(0, np.nan).clip(lower=0.01, upper=15)
df['velocity'] = df['velocity'].fillna(0)

# Geo-distance
city_coords = {
    "New York, NY": (40.7128, -74.0060),
    "London, UK": (51.5074, -0.1278),
    "Tokyo, JP": (35.6762, 139.6503),
    "Los Angeles, CA": (34.0522, -118.2437),
    "Chicago, IL": (41.8781, -87.6298),
    "Miami, FL": (25.7617, -80.1918),
    "Boston, MA": (42.3601, -71.0589),
    "San Francisco, CA": (37.7749, -122.4194),
    "Seattle, WA": (47.6062, -122.3321),
    "Houston, TX": (29.7604, -95.3698)
}
def get_distance(row, prev_locations):
    if row['user_id'] in prev_locations and prev_locations[row['user_id']]:
        prev_loc = prev_locations[row['user_id']][-1]
        curr_loc = city_coords.get(row['location'], city_coords["Boston, MA"])
        prev_loc = city_coords.get(prev_loc, city_coords["Boston, MA"])
        return min(geodesic(curr_loc, prev_loc).km, 1200)
    return 0

df['geo_distance'] = 0.0
prev_locations = {}
for idx, row in df.iterrows():
    if row['user_id'] not in prev_locations:
        prev_locations[row['user_id']] = []
    df.at[idx, 'geo_distance'] = get_distance(row, prev_locations)
    prev_locations[row['user_id']].append(row['location'])

# Save features
features = ['amount', 'hour_of_day', 'velocity', 'geo_distance']
df_features = df[features + ['is_fraud']]
df_features.to_csv(output_path, index=False)
print(f"Features saved to {output_path}")