"""FastMCP weather server for Databricks Apps."""

from __future__ import annotations

import os
from typing import Any, Callable

from fastmcp import FastMCP

from weather_adapter import OpenMeteoAdapter, WeatherAdapterError

mcp = FastMCP(
    "Weather Prediction MCP",
    instructions=(
        "Use these tools for current conditions, forecasts, and deterministic travel "
        "recommendations. Never invent weather data when a tool returns an error."
    ),
)


def _run(operation: Callable[[OpenMeteoAdapter], dict[str, Any]]) -> dict[str, Any]:
    try:
        with OpenMeteoAdapter() as adapter:
            return {"ok": True, "data": operation(adapter)}
    except WeatherAdapterError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception:
        return {
            "ok": False,
            "error": "An unexpected weather service error occurred. Try again shortly.",
        }


@mcp.tool
def get_current_weather(location: str) -> dict[str, Any]:
    """Get current modeled weather conditions for a location.

    Args:
        location: City/postal-code text or a `latitude,longitude` pair.

    Returns:
        A structured result containing temperature, conditions, humidity,
        precipitation, and wind, or a clean error object.
    """
    return _run(lambda adapter: adapter.current_weather(location))


@mcp.tool
def get_forecast(location: str, days: int = 7) -> dict[str, Any]:
    """Get a daily weather forecast for the next 1 through 16 days.

    Args:
        location: City/postal-code text or a `latitude,longitude` pair.
        days: Number of forecast days, from 1 through 16.

    Returns:
        Daily conditions, highs, lows, precipitation probability, precipitation
        amount, and maximum wind, or a clean error object.
    """
    return _run(lambda adapter: adapter.forecast(location, days))


@mcp.tool
def get_travel_recommendation(location: str, date: str) -> dict[str, Any]:
    """Recommend weather precautions using transparent forecast thresholds.

    Umbrella/waterproof protection is recommended at >=40% precipitation
    probability; a warm jacket below 10°C; a light jacket when the high is below
    18°C; heat precautions at >=28°C; and wind precautions at >=40 km/h.

    Args:
        location: City/postal-code text or a `latitude,longitude` pair.
        date: Local forecast date in YYYY-MM-DD format, from today through the
            next 15 days.

    Returns:
        Forecast evidence, recommendations, reasoning, and applied thresholds,
        or a clean error object.
    """
    return _run(lambda adapter: adapter.travel_recommendation(location, date))


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("DATABRICKS_APP_PORT", os.getenv("PORT", "8000"))),
        path=os.getenv("MCP_PATH", "/mcp"),
    )
