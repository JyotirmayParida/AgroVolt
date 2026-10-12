from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.db import Farm, Prediction, SensorData
from app.models.schemas import FarmCreate, SensorDataCreate


def get_all_farms(db: Session):
    return db.query(Farm).all()


def get_farm_by_id(db: Session, farm_id: int):
    return db.query(Farm).filter(Farm.id == farm_id).first()


def create_farm(db: Session, farm: FarmCreate):
    db_farm = Farm(**farm.model_dump())
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm


def save_prediction(db: Session, farm_id: int, yield_val: float,
                    solar_kwh: float, irrigation: str):
    pred = Prediction(
        farm_id=farm_id,
        predicted_yield=yield_val,
        predicted_solar_kwh=solar_kwh,
        irrigation_recommendation=irrigation,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def get_predictions_by_farm(db: Session, farm_id: int):
    return (
        db.query(Prediction)
        .filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.timestamp.desc())
        .all()
    )


def save_sensor_data(db: Session, data: SensorDataCreate):
    sensor = SensorData(**data.model_dump())
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


def get_sensor_data_by_farm(db: Session, farm_id: int):
    return (
        db.query(SensorData)
        .filter(SensorData.farm_id == farm_id)
        .order_by(SensorData.timestamp.desc())
        .all()
    )