"""
Simple ML Model Training Script
Trains a Random Forest model on test data and saves it as pickle file
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# Configuration
WORKSPACE_DIR = Path("/Users/jisnyvarghese/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd")
TEST_RESPONSES_FILE = WORKSPACE_DIR / "test_responses.json"
MODEL_FILE = WORKSPACE_DIR / "assertion_model.pkl"

print("=" * 60)
print("AI-Powered Test Oracle: Simple ML Model Training")
print("=" * 60)

# Load data
print("\n📂 Loading test data...")
with open(TEST_RESPONSES_FILE, 'r') as f:
    all_responses = json.load(f)
print(f"✓ Loaded {len(all_responses)} test responses")

# Parse XML and extract features
print("\n🔧 Extracting features...")
features_list = []

for response in all_responses:
    try:
        content = response.get('content', '')
        if not content:
            continue
            
        root = ET.fromstring(content)
        
        test_name = root.get('name', '').lower()
        execution_time = float(root.get('time', '0'))
        
        # Extract features
        features = {
            'execution_time_target': execution_time,
            'has_get': 1 if 'get' in test_name else 0,
            'has_post': 1 if 'post' in test_name else 0,
            'has_put': 1 if 'put' in test_name else 0,
            'has_delete': 1 if 'delete' in test_name else 0,
            'has_query': 1 if 'query' in test_name else 0,
            'has_mutation': 1 if 'mutation' in test_name else 0,
            'test_name_length': len(test_name),
            'api_type': 1 if response.get('api_type') == 'REST' else 0
        }
        
        features_list.append(features)
    except:
        continue

df = pd.DataFrame(features_list)
print(f"✓ Extracted features from {len(df)} samples")

if len(df) < 10:
    print(f"\n❌ Not enough data ({len(df)} samples). Need at least 10 samples.")
    print("   Please run fetch_test_data.py to collect more test data.")
    exit(1)

# Prepare training data
print("\n📊 Preparing training data...")
feature_columns = [col for col in df.columns if col != 'execution_time_target']
X = df[feature_columns]
y = df['execution_time_target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"  Training samples: {len(X_train)}")
print(f"  Test samples: {len(X_test)}")
print(f"  Features: {len(feature_columns)}")

# Train model
print("\n🤖 Training Random Forest Regressor...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("✓ Model trained successfully")

# Evaluate
print("\n📊 Evaluating model...")
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"  Mean Squared Error: {mse:.4f}")
print(f"  R² Score: {r2:.4f}")

# Feature importance
print("\n📈 Top 5 Feature Importances:")
feature_importance = sorted(
    zip(feature_columns, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True
)
for i, (feature, importance) in enumerate(feature_importance[:5], 1):
    print(f"  {i}. {feature}: {importance:.4f}")

# Save model
print("\n💾 Saving model...")
model_package = {
    'model': model,
    'model_name': 'Random Forest Regressor',
    'score': r2,
    'is_regression': True,
    'feature_columns': feature_columns,
    'training_date': datetime.now().isoformat(),
    'num_training_samples': len(X_train),
    'num_test_samples': len(X_test)
}

with open(MODEL_FILE, 'wb') as f:
    pickle.dump(model_package, f)

print(f"✓ Model saved to: {MODEL_FILE}")

# Test loading
print("\n🧪 Testing saved model...")
with open(MODEL_FILE, 'rb') as f:
    loaded_package = pickle.load(f)

loaded_model = loaded_package['model']
sample_pred = loaded_model.predict(X_test.iloc[0:1])

print(f"✓ Model loaded successfully")
print(f"  Sample prediction: {sample_pred[0]:.3f}s")
print(f"  Actual value: {y_test.iloc[0]:.3f}s")
print(f"  Error: {abs(sample_pred[0] - y_test.iloc[0]):.3f}s")

print("\n" + "=" * 60)
print("✅ Training complete! Model saved as assertion_model.pkl")
print("=" * 60)

# Made with Bob
