import os
import tempfile
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, get_db
from app.main import app
import app.ml.crop_model as crop_module
import app.ml.irrigation_model as irrigation_module
from app.utils.nasa_api import get_solar_irradiance
from app.utils.weather_api import get_weather


# Set up isolated in-memory/temp SQLite database for test suite so real app data is NEVER touched
test_temp_db = tempfile.NamedTemporaryFile(suffix="_test.db", delete=False)
test_db_path = test_temp_db.name
test_temp_db.close()

test_engine = create_engine(
    f"sqlite:///{test_db_path}",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ─── Baseline API & ML Tests ────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AgroVolt" in response.json()["message"]


def test_crop_prediction_direct():
    res = crop_module.predict_crop_yield(
        shading_pct=25.0,
        temperature=28.0,
        soil_moisture=50.0,
        rainfall=60.0,
        crop_type_encoded=0,
        panel_tilt=15.0
    )
    assert "predicted_yield_kg_per_hectare" in res
    assert "land_equivalent_ratio" in res
    assert res["predicted_yield_kg_per_hectare"] > 0


def test_crop_predict_api():
    payload = {
        "shading_pct": 25.0,
        "temperature": 28.0,
        "soil_moisture": 50.0,
        "rainfall": 60.0,
        "crop_type_encoded": 0,
        "panel_tilt": 15.0
    }
    response = client.post("/api/crop/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_yield_kg_per_hectare" in data
    assert "land_equivalent_ratio" in data


def test_crop_types():
    response = client.get("/api/crop/crop-types")
    assert response.status_code == 200
    assert len(response.json()["crop_types"]) == 4


def test_irrigation_recommendation_direct():
    res = irrigation_module.recommend_irrigation(
        soil_moisture=15.0,
        temperature=35.0,
        crop_type_encoded=0,
        rainfall_last_24h=0.0,
        time_of_day=14
    )
    assert "recommendation" in res
    assert "confidence" in res


def test_irrigation_api():
    payload = {
        "soil_moisture": 15.0,
        "temperature": 35.0,
        "crop_type_encoded": 0,
        "rainfall_last_24h": 0.0,
        "time_of_day": 14
    }
    response = client.post("/api/irrigation/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendation" in data
    assert data["recommendation"] in ["irrigate_now", "irrigate_in_2h", "no_irrigation"]


def test_solar_forecast_direct():
    from app.ml.solar_model import forecast_solar_output
    res = forecast_solar_output(
        latitude=28.6139,
        longitude=77.2090,
        panel_count=100,
        panel_watt_peak=400.0
    )
    assert len(res["forecast_7_days"]) == 7
    assert res["total_kwh"] > 0


def test_solar_forecast_api():
    payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "panel_count": 100,
        "panel_watt_peak": 400.0
    }
    response = client.post("/api/solar/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["forecast_7_days"]) == 7
    assert data["total_kwh"] > 0


# ─── Farm CRUD & Non-Existent Farm Tests ────────────────────────────────────

def test_farms_crud_api():
    farm_data = {
        "name": "QA Farm Alpha",
        "location": "Punjab, India",
        "latitude": 30.7333,
        "longitude": 76.7794,
        "panel_count": 250,
        "crop_type": "Wheat",
        "area_hectares": 2.5
    }
    response = client.post("/api/farms/", json=farm_data)
    assert response.status_code == 200
    created = response.json()
    farm_id = created["id"]
    assert created["name"] == "QA Farm Alpha"

    # Fetch farm
    get_res = client.get(f"/api/farms/{farm_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "QA Farm Alpha"

    # List farms
    list_res = client.get("/api/farms/")
    assert list_res.status_code == 200
    assert any(f["id"] == farm_id for f in list_res.json())


def test_farm_not_found():
    response = client.get("/api/farms/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found"

    # Predictions for non-existent farm
    pred_res = client.get("/api/farms/999999/predictions")
    assert pred_res.status_code == 404
    assert pred_res.json()["detail"] == "Farm not found"

    # Sensor data for non-existent farm
    sensor_res = client.get("/api/farms/999999/sensor-data")
    assert sensor_res.status_code == 404
    assert sensor_res.json()["detail"] == "Farm not found"


# ─── Sensor Data & Prediction API Workflows ─────────────────────────────────

def test_sensor_data_storage_and_retrieval():
    # 1. Create a farm
    farm_res = client.post("/api/farms/", json={
        "name": "Sensor Test Farm",
        "location": "Gujarat, India",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "panel_count": 100,
        "crop_type": "Rice",
        "area_hectares": 1.2
    })
    assert farm_res.status_code == 200
    farm_id = farm_res.json()["id"]

    # 2. Post sensor readings
    reading = {
        "farm_id": farm_id,
        "soil_moisture": 38.5,
        "temperature": 29.1,
        "shading_pct": 22.0
    }
    post_res = client.post("/api/farms/sensor-data", json=reading)
    assert post_res.status_code == 200
    sensor_saved = post_res.json()
    assert sensor_saved["farm_id"] == farm_id
    assert sensor_saved["soil_moisture"] == 38.5

    # 3. Retrieve sensor history
    history_res = client.get(f"/api/farms/{farm_id}/sensor-data")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert history[0]["soil_moisture"] == 38.5


def test_sensor_data_invalid_farm():
    reading = {
        "farm_id": 999999,
        "soil_moisture": 30.0,
        "temperature": 25.0,
        "shading_pct": 20.0
    }
    post_res = client.post("/api/farms/sensor-data", json=reading)
    assert post_res.status_code == 404
    assert post_res.json()["detail"] == "Farm not found"


def test_prediction_storage_and_history():
    # 1. Create a farm
    farm_res = client.post("/api/farms/", json={
        "name": "Prediction History Farm",
        "location": "Maharashtra, India",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "panel_count": 150,
        "crop_type": "Vegetables",
        "area_hectares": 2.0
    })
    farm_id = farm_res.json()["id"]

    # 2. Record prediction
    pred_data = {
        "farm_id": farm_id,
        "predicted_yield": 4650.0,
        "predicted_solar_kwh": 210.5,
        "irrigation_recommendation": "irrigate_in_2h"
    }
    post_res = client.post(f"/api/farms/{farm_id}/predictions", json=pred_data)
    assert post_res.status_code == 200
    created_pred = post_res.json()
    assert created_pred["predicted_yield"] == 4650.0
    assert created_pred["irrigation_recommendation"] == "irrigate_in_2h"

    # 3. Retrieve prediction history
    history_res = client.get(f"/api/farms/{farm_id}/predictions")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert history[0]["predicted_yield"] == 4650.0


# ─── Input Validation Tests (Bad Payloads) ──────────────────────────────────

def test_invalid_crop_request():
    # Negative shading percentage
    res = client.post("/api/crop/predict", json={
        "shading_pct": -10.0,
        "temperature": 25.0,
        "soil_moisture": 40.0,
        "rainfall": 20.0,
        "crop_type_encoded": 0,
        "panel_tilt": 15.0
    })
    assert res.status_code == 422


def test_invalid_solar_request():
    # Invalid latitude > 90
    res = client.post("/api/solar/forecast", json={
        "latitude": 120.0,
        "longitude": 75.0,
        "panel_count": 50,
        "panel_watt_peak": 350.0
    })
    assert res.status_code == 422


def test_invalid_irrigation_request():
    # Invalid hour (time_of_day = 25)
    res = client.post("/api/irrigation/recommend", json={
        "soil_moisture": 30.0,
        "temperature": 25.0,
        "crop_type_encoded": 0,
        "rainfall_last_24h": 0.0,
        "time_of_day": 25
    })
    assert res.status_code == 422


def test_invalid_farm_create():
    # Empty name and negative panel count
    res = client.post("/api/farms/", json={
        "name": "",
        "location": "Somewhere",
        "latitude": 20.0,
        "longitude": 80.0,
        "panel_count": -5,
        "crop_type": "Wheat",
        "area_hectares": -1.0
    })
    assert res.status_code == 422


# ─── Missing Model Artifacts & Fallback Tests ───────────────────────────────

def test_crop_model_fallback():
    # Temporarily simulate missing model artifact
    original_model = crop_module.model
    try:
        crop_module.model = None
        result = crop_module.predict_crop_yield(
            shading_pct=30.0,
            temperature=25.0,
            soil_moisture=45.0,
            rainfall=20.0,
            crop_type_encoded=0,
            panel_tilt=15.0
        )
        assert "predicted_yield_kg_per_hectare" in result
        assert result["predicted_yield_kg_per_hectare"] > 0
        assert result["land_equivalent_ratio"] == 1.12
    finally:
        crop_module.model = original_model


def test_irrigation_model_fallback():
    original_model = irrigation_module.model
    try:
        irrigation_module.model = None
        result = irrigation_module.recommend_irrigation(
            soil_moisture=15.0,
            temperature=35.0,
            crop_type_encoded=0,
            rainfall_last_24h=0.0,
            time_of_day=14
        )
        assert result["recommendation"] == "irrigate_now"
        assert result["confidence"] == 0.91
    finally:
        irrigation_module.model = original_model


# ─── Weather API Mocking & Error Scenarios ──────────────────────────────────

@pytest.mark.asyncio
async def test_weather_no_api_key():
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": ""}):
        res = await get_weather(28.61, 77.20)
        assert res["temperature"] == 28.5
        assert "demo data" in res["description"]


@pytest.mark.asyncio
async def test_weather_timeout_handling():
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"}):
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Mocked timeout")):
            res = await get_weather(28.61, 77.20)
            assert res["temperature"] is None
            assert "timed out" in res["description"]


@pytest.mark.asyncio
async def test_weather_upstream_http_error():
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"}):
        mock_response = httpx.Response(status_code=401, request=httpx.Request("GET", "http://test"))
        with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPStatusError("Unauthorized", request=mock_response.request, response=mock_response)):
            res = await get_weather(28.61, 77.20)
            assert res["temperature"] is None
            assert "HTTP 401" in res["description"]


@pytest.mark.asyncio
async def test_weather_success_response():
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"}):
        mock_json = {
            "main": {"temp": 26.4, "humidity": 55},
            "weather": [{"description": "few clouds"}],
            "wind": {"speed": 4.1},
            "rain": {"1h": 1.2},
            "name": "New Delhi"
        }
        mock_response = httpx.Response(status_code=200, json=mock_json, request=httpx.Request("GET", "http://test"))
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            res = await get_weather(28.61, 77.20)
            assert res["temperature"] == 26.4
            assert res["humidity"] == 55
            assert res["description"] == "Few Clouds"
            assert res["rainfall"] == 1.2
            assert res["location"] == "New Delhi"


# ─── NASA POWER API Mocking & Error Scenarios ───────────────────────────────

@pytest.mark.asyncio
async def test_nasa_power_success_response():
    mock_json = {
        "properties": {
            "parameter": {
                "ALLSKY_SFC_SW_DWN": {
                    "20261001": 5.4,
                    "20261002": 5.2,
                    "20261003": -999.0,  # fill value to be filtered
                    "20261004": 6.1
                }
            }
        }
    }
    mock_response = httpx.Response(status_code=200, json=mock_json, request=httpx.Request("GET", "http://test"))
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        res = await get_solar_irradiance(28.61, 77.20)
        assert res["unit"] == "kWh/m²/day"
        assert -999.0 not in res["irradiance_30_days"]
        assert res["irradiance_30_days"] == [5.4, 5.2, 6.1]


@pytest.mark.asyncio
async def test_nasa_power_timeout_handling():
    with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Mocked NASA timeout")):
        res = await get_solar_irradiance(28.61, 77.20)
        assert len(res["irradiance_30_days"]) == 30
        assert "NASA API timed out" in res["unit"]


@pytest.mark.asyncio
async def test_nasa_power_upstream_http_error():
    mock_response = httpx.Response(status_code=500, request=httpx.Request("GET", "http://test"))
    with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPStatusError("Server Error", request=mock_response.request, response=mock_response)):
        res = await get_solar_irradiance(28.61, 77.20)
        assert len(res["irradiance_30_days"]) == 30
        assert "HTTP 500" in res["unit"]
