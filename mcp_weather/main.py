from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

API_WEATHER_GOV_BASE = "https://api.weather.gov"

mcp = FastMCP("mcp_weather")

async def fetch_weather_data(url: str) -> dict:
    headers = {"User-Agent": "weather-app/1.0"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch weather data: {resp.status_code}")
        return resp.json()

@mcp.tool()
async def get_weather(lat: float, lon: float, city: str = None) -> dict[str, Any]:
    """
    Get the current weather forecast for a given latitude and longitude using the US National Weather Service API.
    Optionally include a city name for reference in the response.
    Returns temperature and short forecast description for the location.
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
    Get the weather forecast for a given latitude and longitude using the US National Weather Service API.
    Returns temperature and short forecast description for the location.
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
    Get active weather alerts for a given US state using the US National Weather Service API.
    Returns a list of alerts with event, headline, and description.
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
    print("Starting MCP Weather server...")
    # You may want to register get_weather as an MCP method here, depending on FastMCP usage
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
