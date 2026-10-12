from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import crud
from app.database.db import get_db
from app.models.schemas import (
    FarmCreate,
    FarmResponse,
    PredictionCreate,
    PredictionResponse,
    SensorDataCreate,
    SensorDataResponse,
)

router = APIRouter()


@router.get("/", response_model=List[FarmResponse])
def get_farms(db: Session = Depends(get_db)):
    """Return all farms."""
    return crud.get_all_farms(db)


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    """Return a specific farm by ID."""
    farm = crud.get_farm_by_id(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@router.post("/", response_model=FarmResponse)
def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    """Add a new farm."""
    return crud.create_farm(db, farm)


@router.get("/{farm_id}/predictions", response_model=List[PredictionResponse])
def get_farm_predictions(farm_id: int, db: Session = Depends(get_db)):
    """Get all predictions history for a farm."""
    farm = crud.get_farm_by_id(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return crud.get_predictions_by_farm(db, farm_id)


@router.post("/{farm_id}/predictions", response_model=PredictionResponse)
def post_farm_prediction(farm_id: int, data: PredictionCreate, db: Session = Depends(get_db)):
    """Record a prediction in history for a farm."""
    farm = crud.get_farm_by_id(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return crud.save_prediction(
        db,
        farm_id=farm_id,
        yield_val=data.predicted_yield,
        solar_kwh=data.predicted_solar_kwh,
        irrigation=data.irrigation_recommendation,
    )


@router.post("/sensor-data", response_model=SensorDataResponse)
def post_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """
    Endpoint for IoT sensors to push real-time readings.
    In production, sensors POST here on a schedule.
    """
    farm = crud.get_farm_by_id(db, data.farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return crud.save_sensor_data(db, data)


@router.get("/{farm_id}/sensor-data", response_model=List[SensorDataResponse])
def get_farm_sensor_data(farm_id: int, db: Session = Depends(get_db)):
    """Get all sensor data history for a farm."""
    farm = crud.get_farm_by_id(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return crud.get_sensor_data_by_farm(db, farm_id)
