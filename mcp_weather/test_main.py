"""
Unit tests for mcp_weather tools.

These tests use pytest and monkeypatching to mock network requests for the
get_weather, get_forecast, and get_alerts functions. All tests ensure correct
behavior and output structure for various weather scenarios, without making real
HTTP requests.
"""

import pytest
from main import get_weather, get_forecast, get_alerts

@pytest.mark.asyncio
async def test_get_weather_newtaipei(monkeypatch):
    """
    Test get_weather for New Taipei using a monkeypatched mock to avoid real HTTP requests.
    Verifies correct city, coordinates, temperature, and condition are returned.
    """
    # Mock fetch_weather_data to avoid real HTTP requests
    async def mock_fetch_weather_data(url: str):
        if "points" in url:
            return {
                "properties": {"forecast": "mock_forecast_url"}
            }
        if "mock_forecast_url" in url:
            return {
                "properties": {
                    "periods": [
                        {
                            "temperature": 28,
                            "shortForecast": "Partly Cloudy"
                        }
                    ]
                }
            }
        raise ValueError("Unexpected URL")

    monkeypatch.setattr("main.fetch_weather_data", mock_fetch_weather_data)

    lat = 25.0124
    lon = 121.4657
    city = "New Taipei"
    result = await get_weather(lat, lon, city=city)
    assert result["city"] == city
    assert result["lat"] == lat
    assert result["lon"] == lon
    assert result["temperature"] == 28
    assert result["condition"] == "Partly Cloudy"

@pytest.mark.asyncio
async def test_get_forecast_newtaipei(monkeypatch):
    """
    Test get_forecast for New Taipei using a monkeypatched mock to avoid real HTTP requests.
    Verifies correct coordinates, temperature, and condition are returned.
    """
    async def mock_fetch_weather_data(url: str):
        if "points" in url:
            return {"properties": {"forecast": "mock_forecast_url"}}
        if "mock_forecast_url" in url:
            return {
                "properties": {
                    "periods": [
                        {"temperature": 30, "shortForecast": "Sunny"}
                    ]
                }
            }
        raise ValueError("Unexpected URL")
    monkeypatch.setattr("main.fetch_weather_data", mock_fetch_weather_data)
    lat = 25.0124
    lon = 121.4657
    result = await get_forecast(lat, lon)
    assert result["lat"] == lat
    assert result["lon"] == lon
    assert result["temperature"] == 30
    assert result["condition"] == "Sunny"

@pytest.mark.asyncio
async def test_get_alerts_dc(monkeypatch):
    """
    Test get_alerts for DC using a monkeypatched mock to avoid real HTTP requests.
    Verifies correct state and alert events are returned.
    """
    async def mock_fetch_weather_data(url: str):
        if "alerts/active" in url:
            return {
                "features": [
                    {
                        "properties": {
                            "event": "Flood Warning",
                            "headline": "Flooding expected",
                            "description": "Heavy rain in DC."
                        }
                    },
                    {
                        "properties": {
                            "event": "Heat Advisory",
                            "headline": "High temperatures",
                            "description": "Stay hydrated."
                        }
                    }
                ]
            }
        raise ValueError("Unexpected URL")
    monkeypatch.setattr("main.fetch_weather_data", mock_fetch_weather_data)
    state = "DC"
    result = await get_alerts(state)
    assert result["state"] == state
    assert len(result["alerts"]) == 2
    assert result["alerts"][0]["event"] == "Flood Warning"
    assert result["alerts"][1]["event"] == "Heat Advisory"
