"""
MCP Weather Server
------------------

This module provides AI/LLM-friendly tools for fetching current weather, forecasts, and alerts
for US locations using the US National Weather Service API.

Tools:
- get_weather: Get current weather for a latitude/longitude (optionally with city name).
- get_forecast: Get forecast for a latitude/longitude.
- get_alerts: Get active weather alerts for a US state.

Intended for use in Model Context Protocol (MCP) servers and AI assistant environments.
"""

from typing import Any
import httpx
from httpx import HTTPStatusError
from mcp.server.fastmcp import FastMCP

API_WEATHER_GOV_BASE = "https://api.weather.gov"

mcp = FastMCP("mcp_weather")

async def fetch_weather_data(url: str) -> dict:
    """
    Fetch weather data from the specified URL using an asynchronous HTTP GET request.

    Args:
        url (str): The URL to fetch weather data from.

    Returns:
        dict: The JSON response as a dictionary if the request is successful.

    Raises:
        HTTPStatusError: If the HTTP response status code is not 200.
    """
    headers = {"User-Agent": "weather-app/1.0"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPStatusError(
                f"Failed to fetch weather data: {resp.status_code}",
                request=resp.request,
                response=resp
            )
        return resp.json()

@mcp.tool()
async def get_weather(lat: float, lon: float, city: str = None) -> dict[str, Any]:
    """
    AI Tool: get_weather
    ---------------------
    Returns the current weather forecast for a given latitude and longitude in the US, using
    the US National Weather Service API. Optionally includes a city name for reference in the
    response.

    This tool is designed for use by AI assistants and LLMs to provide up-to-date weather
    information, including temperature and a short forecast description, for any US location
    specified by coordinates.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        city (str, optional): City name for reference (not used in the API call).

    Returns:
        dict: {
            'city': city name (if provided),
            'lat': latitude,
            'lon': longitude,
            'temperature': current temperature,
            'condition': short weather description
        }
    """
    url = f"{API_WEATHER_GOV_BASE}/points/{lat},{lon}"
    data = await fetch_weather_data(url)
    forecast_url = data["properties"]["forecast"]
    forecast_data = await fetch_weather_data(forecast_url)
    period = forecast_data["properties"]["periods"][0]
    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "temperature": period["temperature"],
        "condition": period["shortForecast"]
    }

@mcp.tool()
async def get_forecast(lat: float, lon: float) -> dict[str, Any]:
    """
    AI Tool: get_forecast
    ---------------------
    Returns the weather forecast for a given latitude and longitude in the US, using the US
    National Weather Service API.

    This tool is designed for use by AI assistants and LLMs to provide up-to-date forecast
    information, including temperature and a short forecast description, for any US location
    specified by coordinates.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: {
            'lat': latitude,
            'lon': longitude,
            'temperature': forecasted temperature,
            'condition': short weather description
        }
    """
    url = f"{API_WEATHER_GOV_BASE}/points/{lat},{lon}"
    data = await fetch_weather_data(url)
    forecast_url = data["properties"]["forecast"]
    forecast_data = await fetch_weather_data(forecast_url)
    period = forecast_data["properties"]["periods"][0]
    return {
        "lat": lat,
        "lon": lon,
        "temperature": period["temperature"],
        "condition": period["shortForecast"]
    }

@mcp.tool()
async def get_alerts(state: str = "DC") -> dict[str, Any]:
    """
    AI Tool: get_alerts
    -------------------
    Returns active weather alerts for a given US state using the US National Weather Service API.

    This tool is designed for use by AI assistants and LLMs to provide up-to-date weather alerts,
    including event, headline, and description, for any US state specified by its abbreviation
    (e.g., 'CA', 'NY').

    Args:
        state (str): The two-letter US state abbreviation (default: 'DC').

    Returns:
        dict: {
            'state': state abbreviation,
            'alerts': [
                {
                    'event': event name,
                    'headline': alert headline,
                    'description': alert description
                },
                ...
            ]
        }
    """
    # Fetch alerts for a state (e.g., DC, MD, VA)
    url = f"{API_WEATHER_GOV_BASE}/alerts/active?area={state}"
    data = await fetch_weather_data(url)
    alerts = data.get("features", [])
    return {
        "state": state,
        "alerts": [
            {
                "event": alert["properties"].get("event"),
                "headline": alert["properties"].get("headline"),
                "description": alert["properties"].get("description")
            }
            for alert in alerts
        ]
    }

def main():
    """
    Entry point for the MCP Weather server.
    Initializes and starts the FastMCP server to expose weather tools for AI/LLM environments.
    """
    print("Starting MCP Weather server...")
    # You may want to register get_weather as an MCP method here, depending on FastMCP usage
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
