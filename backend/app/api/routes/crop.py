from fastapi import APIRouter
from app.models.schemas import CropPredictRequest, CropPredictResponse
from app.ml.crop_model import predict_crop_yield

router = APIRouter()


@router.post("/predict", response_model=CropPredictResponse)
def predict_yield(data: CropPredictRequest):
    """
    Predict crop yield (kg/hectare) based on agrovoltaic farm parameters.
    Uses XGBoost regression model.
    """
    result = predict_crop_yield(
        shading_pct=data.shading_pct,
        temperature=data.temperature,
        soil_moisture=data.soil_moisture,
        rainfall=data.rainfall,
        crop_type_encoded=data.crop_type_encoded,
        panel_tilt=data.panel_tilt
    )
    return result


@router.get("/crop-types")
def get_crop_types():
    """Return the list of supported crop types and their encoded values."""
    return {
        "crop_types": [
            {"id": 0, "name": "Wheat"},
            {"id": 1, "name": "Rice"},
            {"id": 2, "name": "Vegetables"},
            {"id": 3, "name": "Berries"},
        ]
    }
