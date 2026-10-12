import logging
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger("agrovolt.nasa_api")

NASA_BASE = "https://power.larc.nasa.gov/api/temporal/daily/point"


async def get_solar_irradiance(lat: float, lon: float) -> dict:
    """
    Fetch historical solar irradiance from NASA POWER API.
    No API key required — completely free and open.
    Returns last 30 days of data.
    """
    # Dynamically calculate a recent 30-day window
    # NASA POWER data has a ~5 day lag, so we use 7-37 days ago
    now = datetime.now(timezone.utc)
    end_date   = (now - timedelta(days=7)).strftime("%Y%m%d")
    start_date = (now - timedelta(days=37)).strftime("%Y%m%d")

    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",   # Surface solar irradiance
        "community":  "RE",
        "longitude":  lon,
        "latitude":   lat,
        "start":      start_date,
        "end":        end_date,
        "format":     "JSON",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(NASA_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        irradiance = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        # Filter out any fill values (-999)
        values = [v for v in irradiance.values() if v > 0]
        if not values:
            raise ValueError("All irradiance values were fill values")

        return {"irradiance_30_days": values, "unit": "kWh/m²/day"}

    except httpx.TimeoutException:
        logger.warning("NASA POWER request timed out for lat=%s, lon=%s", lat, lon)
        mock_vals = [4.5 + (i % 7) * 0.3 for i in range(30)]
        return {"irradiance_30_days": mock_vals, "unit": "kWh/m²/day (demo — NASA API timed out)"}
    except httpx.HTTPStatusError as e:
        logger.error("NASA POWER HTTP error %s for lat=%s, lon=%s", e.response.status_code, lat, lon)
        mock_vals = [4.5 + (i % 7) * 0.3 for i in range(30)]
        return {"irradiance_30_days": mock_vals, "unit": f"kWh/m²/day (demo — HTTP {e.response.status_code})"}
    except Exception as e:
        logger.warning("NASA POWER API error: %s — returning demo data", e)
        mock_vals = [4.5 + (i % 7) * 0.3 for i in range(30)]
        return {"irradiance_30_days": mock_vals, "unit": "kWh/m²/day (demo)"}
