from fastapi import APIRouter
from app.models.schemas import SolarForecastRequest, SolarForecastResponse
from app.ml.solar_model import forecast_solar_output
from app.utils.nasa_api import get_solar_irradiance

router = APIRouter()


@router.post("/forecast", response_model=SolarForecastResponse)
def solar_forecast(data: SolarForecastRequest):
    """
    Forecast 7-day solar energy output (kWh) for a given farm location.
    Uses LSTM model trained on NASA POWER data.
    """
    result = forecast_solar_output(
        latitude=data.latitude,
        longitude=data.longitude,
        panel_count=data.panel_count,
        panel_watt_peak=data.panel_watt_peak
    )
    return result


@router.get("/irradiance")
async def get_irradiance(lat: float, lon: float):
    """
    Get raw solar irradiance data from NASA POWER API.
    No API key required.
    """
    data = await get_solar_irradiance(lat, lon)
    return data
