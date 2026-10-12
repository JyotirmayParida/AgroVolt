from fastapi import APIRouter
from app.utils.weather_api import get_weather

router = APIRouter()


@router.get("/{lat}/{lon}")
async def weather(lat: float, lon: float):
    """
    Fetch current weather for a farm location.
    Uses OpenWeatherMap API (add key in .env).
    Returns temperature, humidity, rainfall, wind speed.
    """
    data = await get_weather(lat, lon)
    return data
