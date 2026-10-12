import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("agrovolt.weather_api")


async def get_weather(lat: float, lon: float) -> dict:
    """Fetch current weather from OpenWeatherMap."""
    owm_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not owm_key:
        logger.info("No OPENWEATHER_API_KEY set — returning mock weather data")
        return {
            "temperature": 28.5,
            "humidity": 62,
            "rainfall": 0.0,
            "description": "Clear sky (demo data — set OPENWEATHER_API_KEY in .env for live weather)",
            "wind_speed": 3.2,
            "location": f"Lat {lat}, Lon {lon}",
        }

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={owm_key}&units=metric"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        return {
            "temperature":  data["main"]["temp"],
            "humidity":     data["main"]["humidity"],
            "rainfall":     data.get("rain", {}).get("1h", 0.0),
            "description":  data["weather"][0]["description"].title(),
            "wind_speed":   data["wind"]["speed"],
            "location":     data.get("name", "Unknown"),
        }
    except httpx.TimeoutException:
        logger.warning("OpenWeatherMap request timed out for lat=%s, lon=%s", lat, lon)
        return {
            "temperature": None,
            "humidity": None,
            "rainfall": None,
            "description": "Weather service timed out. Try again later.",
            "wind_speed": None,
            "location": f"Lat {lat}, Lon {lon}",
        }
    except httpx.HTTPStatusError as e:
        logger.error("OpenWeatherMap HTTP error %s for lat=%s, lon=%s", e.response.status_code, lat, lon)
        return {
            "temperature": None,
            "humidity": None,
            "rainfall": None,
            "description": f"Weather service error (HTTP {e.response.status_code})",
            "wind_speed": None,
            "location": f"Lat {lat}, Lon {lon}",
        }
    except Exception as e:
        logger.error("Unexpected weather API error: %s", e)
        return {
            "temperature": None,
            "humidity": None,
            "rainfall": None,
            "description": "Weather data unavailable",
            "wind_speed": None,
            "location": f"Lat {lat}, Lon {lon}",
        }
