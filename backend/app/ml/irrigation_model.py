import logging
import os
from pathlib import Path

import numpy as np

logger = logging.getLogger("agrovolt.irrigation_model")

# Resolve model path relative to the backend directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = _BACKEND_DIR / "models_saved" / "irrigation_model.pkl"

model = None

try:
    import joblib
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        logger.info("Irrigation model loaded from %s", MODEL_PATH)
    else:
        logger.warning("No saved irrigation model at %s — using rule-based fallback", MODEL_PATH)
except Exception as e:
    logger.error("Irrigation model load error: %s", e)


LABELS = {
    0: ("irrigate_now",    "💧 Irrigate Now",        "Soil moisture critically low."),
    1: ("irrigate_in_2h",  "⏰ Irrigate in 2 Hours", "Moisture dropping. Schedule soon."),
    2: ("no_irrigation",   "✅ No Irrigation Needed", "Soil moisture is adequate."),
}


def recommend_irrigation(soil_moisture: float, temperature: float,
                         crop_type_encoded: int, rainfall_last_24h: float,
                         time_of_day: int) -> dict:
    """
    Classify irrigation need into 3 classes.
    Uses Random Forest if trained; else rule-based logic.
    """
    if model is not None:
        import pandas as pd
        features = pd.DataFrame([{
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "crop_type_encoded": crop_type_encoded,
            "rainfall_last_24h": rainfall_last_24h,
            "time_of_day": time_of_day
        }])
        label_idx  = int(model.predict(features)[0])
        proba      = float(model.predict_proba(features).max())
    else:
        # Rule-based fallback (deterministic)
        if soil_moisture < 25 and rainfall_last_24h < 5:
            label_idx = 0
        elif soil_moisture < 45 and temperature > 30:
            label_idx = 1
        else:
            label_idx = 2

        # Fallback confidence — clearly NOT a calibrated model probability
        proba = 0.91 if label_idx == 0 else (0.84 if label_idx == 1 else 0.92)

    code, label, reason = LABELS.get(label_idx, LABELS[2])

    return {
        "recommendation": code,
        "label": label,
        "reason": reason,
        "confidence": round(proba, 2),
    }
