import logging
import os
from pathlib import Path

import numpy as np

logger = logging.getLogger("agrovolt.crop_model")

# Resolve model path relative to the backend directory (parent of app/)
# This works regardless of the CWD when launching the application.
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = _BACKEND_DIR / "models_saved" / "crop_model.pkl"

model = None

try:
    import joblib
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        logger.info("Crop model loaded from %s", MODEL_PATH)
    else:
        logger.warning("No saved crop model found at %s — using formula fallback", MODEL_PATH)
except Exception as e:
    logger.error("Crop model load error: %s", e)


CROP_BASE_YIELDS = {
    0: 3500,   # wheat
    1: 4800,   # rice
    2: 6000,   # vegetables
    3: 2200,   # berries
}


def predict_crop_yield(shading_pct: float, temperature: float, soil_moisture: float,
                       rainfall: float, crop_type_encoded: int, panel_tilt: float) -> dict:
    """
    Predict crop yield in kg/hectare.
    Uses XGBoost model if trained; otherwise uses agronomic formula.
    """
    if model is not None:
        import pandas as pd
        features = pd.DataFrame([{
            "shading_pct": shading_pct,
            "temperature": temperature,
            "soil_moisture": soil_moisture,
            "rainfall": rainfall,
            "crop_type_encoded": crop_type_encoded,
            "panel_tilt": panel_tilt
        }])
        yield_pred = float(model.predict(features)[0])
    else:
        # Formula fallback (deterministic, for demo use)
        base = CROP_BASE_YIELDS.get(crop_type_encoded, 4000)
        shade_factor  = 1 + (0.15 if 20 <= shading_pct <= 40 else -0.1)
        temp_factor   = 1 - abs(temperature - 25) * 0.01
        moist_factor  = 1 + (soil_moisture - 40) * 0.005
        rain_factor   = 1 + min(rainfall, 100) * 0.002
        yield_pred = base * shade_factor * temp_factor * moist_factor * rain_factor

    # Land Equivalent Ratio: agrovoltaic land efficiency metric
    # LER > 1 means dual-use is better than separate plots
    ler = round(1 + (shading_pct * 0.004), 2)

    # Advice
    if yield_pred > 5000:
        rec = "Excellent conditions. Maintain current panel configuration."
    elif yield_pred > 3000:
        rec = "Good yield. Consider increasing shading slightly to reduce heat stress."
    else:
        rec = "Low yield. Reduce shading or switch to shade-tolerant crops."

    return {
        "predicted_yield_kg_per_hectare": round(yield_pred, 2),
        "land_equivalent_ratio": ler,
        "recommendation": rec,
    }
