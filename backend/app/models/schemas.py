from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ─── Crop ────────────────────────────────────────────────────────────────────

class CropPredictRequest(BaseModel):
    shading_pct: float = Field(..., ge=0, le=100, description="Panel shading percentage (0–100)")
    temperature: float = Field(..., description="Temperature in Celsius")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage (0–100)")
    rainfall: float = Field(..., ge=0, description="Rainfall in mm")
    crop_type_encoded: int = Field(..., ge=0, le=3, description="0=wheat, 1=rice, 2=vegetables, 3=berries")
    panel_tilt: float = Field(..., ge=0, le=90, description="Panel tilt degrees (0–90)")

class CropPredictResponse(BaseModel):
    predicted_yield_kg_per_hectare: float
    land_equivalent_ratio: float
    recommendation: str


# ─── Solar ───────────────────────────────────────────────────────────────────

class SolarForecastRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    panel_count: int = Field(..., ge=1)
    panel_watt_peak: float = Field(..., gt=0, description="Watts per panel")

class SolarDayForecast(BaseModel):
    day: int
    kwh: float

class SolarForecastResponse(BaseModel):
    forecast_7_days: List[float]
    total_kwh: float
    avg_daily_kwh: float


# ─── Irrigation ──────────────────────────────────────────────────────────────

class IrrigationRequest(BaseModel):
    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float
    crop_type_encoded: int = Field(..., ge=0, le=3)
    rainfall_last_24h: float = Field(..., ge=0)
    time_of_day: int = Field(..., ge=0, le=23, description="Hour in 24h format (0–23)")

class IrrigationResponse(BaseModel):
    recommendation: str         # "irrigate_now", "irrigate_in_2h", "no_irrigation"
    label: str                  # Human readable
    reason: str                 # Explanation of the recommendation
    confidence: float


# ─── Farm ────────────────────────────────────────────────────────────────────

class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    panel_count: int = Field(..., ge=0)
    crop_type: str = Field(..., min_length=1, max_length=50)
    area_hectares: float = Field(..., gt=0)

class FarmResponse(BaseModel):
    id: int
    name: str
    location: str
    latitude: float
    longitude: float
    panel_count: int
    crop_type: str
    area_hectares: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Prediction ──────────────────────────────────────────────────────────────

class PredictionCreate(BaseModel):
    farm_id: int = Field(..., ge=1)
    predicted_yield: Optional[float] = None
    predicted_solar_kwh: Optional[float] = None
    irrigation_recommendation: Optional[str] = None

class PredictionResponse(BaseModel):
    id: int
    farm_id: int
    predicted_yield: Optional[float] = None
    predicted_solar_kwh: Optional[float] = None
    irrigation_recommendation: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# ─── Sensor Data ─────────────────────────────────────────────────────────────

class SensorDataCreate(BaseModel):
    farm_id: int = Field(..., ge=1)
    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float
    shading_pct: float = Field(..., ge=0, le=100)

class SensorDataResponse(BaseModel):
    id: int
    farm_id: int
    soil_moisture: float
    temperature: float
    shading_pct: float
    timestamp: datetime

    model_config = {"from_attributes": True}
