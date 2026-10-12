import hashlib
import logging

import numpy as np

logger = logging.getLogger("agrovolt.solar_model")


def forecast_solar_output(latitude: float, longitude: float,
                           panel_count: int, panel_watt_peak: float) -> dict:
    """
    Forecast 7-day solar energy output.

    Uses a physics-based formula with latitude-dependent peak sun hours
    and deterministic cloud variation (seeded by coordinates for reproducibility).

    Note: The README mentions an intended LSTM model. No LSTM is currently
    implemented or trained — this is a deterministic formula-based forecast.
    """
    # Approximate daily peak sun hours based on latitude
    # Tropical (low lat) → more sun. Higher lat → less sun.
    base_peak_hours = max(3.5, 7.0 - abs(latitude) * 0.05)

    # Deterministic seed from coordinates so the same location gives stable results
    seed_str = f"{latitude:.4f}_{longitude:.4f}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16) % (2**31)
    rng = np.random.RandomState(seed)

    # Simulate 7 days with slight variation (clouds, etc.)
    forecast = []
    for day in range(7):
        cloud_factor = rng.uniform(0.65, 1.0)
        peak_hours   = base_peak_hours * cloud_factor
        daily_kwh    = (panel_count * panel_watt_peak * peak_hours) / 1000
        forecast.append(round(daily_kwh, 2))

    total     = round(sum(forecast), 2)
    avg_daily = round(total / 7, 2)

    return {
        "forecast_7_days": forecast,
        "total_kwh": total,
        "avg_daily_kwh": avg_daily,
    }
