from fastapi import APIRouter
from app.models.schemas import IrrigationRequest, IrrigationResponse
from app.ml.irrigation_model import recommend_irrigation

router = APIRouter()


@router.post("/recommend", response_model=IrrigationResponse)
def irrigation_recommend(data: IrrigationRequest):
    """
    Classify irrigation need using Random Forest model.
    Returns one of: irrigate_now | irrigate_in_2h | no_irrigation
    """
    result = recommend_irrigation(
        soil_moisture=data.soil_moisture,
        temperature=data.temperature,
        crop_type_encoded=data.crop_type_encoded,
        rainfall_last_24h=data.rainfall_last_24h,
        time_of_day=data.time_of_day
    )
    return result
