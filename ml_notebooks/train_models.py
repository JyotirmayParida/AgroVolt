"""
AgroVolt — ML Model Training Script
Run this to train and save all 3 ML models.

Usage:
    cd backend
    python ../ml_notebooks/train_models.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error
import xgboost as xgb
import joblib
import os

os.makedirs("models_saved", exist_ok=True)

print("=" * 50)
print("AgroVolt — Model Training")
print("=" * 50)


# ─────────────────────────────────────────────────
# MODEL 1: Crop Yield (XGBoost Regressor)
# ─────────────────────────────────────────────────
print("\n[1/3] Training Crop Yield Model (XGBoost)...")

np.random.seed(42)
n = 1000

crop_df = pd.DataFrame({
    "shading_pct":        np.random.uniform(10, 50, n),
    "temperature":        np.random.uniform(15, 40, n),
    "soil_moisture":      np.random.uniform(20, 80, n),
    "rainfall":           np.random.uniform(0, 100, n),
    "crop_type_encoded":  np.random.randint(0, 4, n),
    "panel_tilt":         np.random.uniform(5, 30, n),
})

# Synthetic yield formula (agronomy-inspired)
base_yields = [3500, 4800, 6000, 2200]
crop_df["yield_kg_per_hectare"] = (
    crop_df.apply(lambda r: base_yields[int(r.crop_type_encoded)], axis=1)
    * (1 + (crop_df["shading_pct"].between(20, 40).astype(float) * 0.15))
    * (1 - np.abs(crop_df["temperature"] - 25) * 0.01)
    * (1 + (crop_df["soil_moisture"] - 40) * 0.005)
    * (1 + np.minimum(crop_df["rainfall"], 100) * 0.002)
    + np.random.normal(0, 200, n)  # noise
)

X = crop_df.drop("yield_kg_per_hectare", axis=1)
y = crop_df["yield_kg_per_hectare"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

crop_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
crop_model.fit(X_train, y_train)

preds = crop_model.predict(X_test)
mae   = mean_absolute_error(y_test, preds)
print(f"   [+] MAE: {mae:.1f} kg/hectare")

joblib.dump(crop_model, "models_saved/crop_model.pkl")
print("   [+] Saved: models_saved/crop_model.pkl")


# ─────────────────────────────────────────────────
# MODEL 2: Irrigation Recommendation (Random Forest Classifier)
# ─────────────────────────────────────────────────
print("\n[2/3] Training Irrigation Model (Random Forest)...")

irr_df = pd.DataFrame({
    "soil_moisture":     np.random.uniform(10, 90, n),
    "temperature":       np.random.uniform(15, 42, n),
    "crop_type_encoded": np.random.randint(0, 4, n),
    "rainfall_last_24h": np.random.uniform(0, 50, n),
    "time_of_day":       np.random.randint(0, 24, n),
})

# Labels: 0 = irrigate now, 1 = irrigate in 2h, 2 = no irrigation
def label_irrigation(row):
    if row.soil_moisture < 25 and row.rainfall_last_24h < 5:
        return 0
    elif row.soil_moisture < 45 and row.temperature > 30:
        return 1
    else:
        return 2

irr_df["label"] = irr_df.apply(label_irrigation, axis=1)

X2 = irr_df.drop("label", axis=1)
y2 = irr_df["label"]
X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)

irr_model = RandomForestClassifier(n_estimators=100, random_state=42)
irr_model.fit(X2_train, y2_train)

y2_pred = irr_model.predict(X2_test)
print(classification_report(y2_test, y2_pred, target_names=["Irrigate Now", "Irrigate in 2h", "No Irrigation"]))

joblib.dump(irr_model, "models_saved/irrigation_model.pkl")
print("   [+] Saved: models_saved/irrigation_model.pkl")


print("\n" + "=" * 50)
print("[+] All models trained and saved!")
print("   models_saved/crop_model.pkl")
print("   models_saved/irrigation_model.pkl")
print("=" * 50)
print("\nNow start the backend: uvicorn app.main:app --reload")
