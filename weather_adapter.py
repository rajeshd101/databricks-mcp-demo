"""Open-Meteo adapter containing all weather HTTP and parsing logic."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
MAX_FORECAST_DAYS = 16
REQUEST_TIMEOUT_SECONDS = 15.0


class WeatherAdapterError(RuntimeError):
    """Base class for clean, user-facing weather adapter errors."""


class LocationNotFoundError(WeatherAdapterError):
    """Raised when Open-Meteo cannot resolve a supplied location."""


class InvalidWeatherRequestError(WeatherAdapterError):
    """Raised when a request parameter is outside supported bounds."""


WMO_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def weather_description(code: int | None) -> str:
    """Translate a WMO weather code into plain English."""
    if code is None:
        return "Unknown"
    return WMO_DESCRIPTIONS.get(int(code), f"Unknown weather code ({code})")


class OpenMeteoAdapter:
    """Small synchronous client for Open-Meteo geocoding and forecast APIs."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._owns_client = client is None
        self.client = client or httpx.Client(
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "weather-mcp-homework/1.0"},
        )

    def close(self) -> None:
        """Close the internally-created HTTP client."""
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> OpenMeteoAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise WeatherAdapterError("The weather service timed out. Try again shortly.") from exc
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                detail = exc.response.json().get("reason", "")
            except (ValueError, AttributeError):
                pass
            message = "The weather service rejected the request"
            if detail:
                message += f": {detail}"
            raise WeatherAdapterError(message + ".") from exc
        except (httpx.RequestError, ValueError) as exc:
            raise WeatherAdapterError("The weather service is temporarily unavailable.") from exc

        if not isinstance(payload, dict):
            raise WeatherAdapterError("The weather service returned an unexpected response.")
        if payload.get("error"):
            raise WeatherAdapterError(str(payload.get("reason", "Weather service error.")))
        return payload

    def resolve_location(self, location: str) -> dict[str, Any]:
        """Resolve a city/postal code or a `latitude,longitude` pair."""
        query = location.strip()
        if not query:
            raise InvalidWeatherRequestError("Location must not be empty.")

        coordinate_match = re.fullmatch(
            r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*", query
        )
        if coordinate_match:
            latitude, longitude = map(float, coordinate_match.groups())
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                raise InvalidWeatherRequestError(
                    "Coordinates must use latitude -90..90 and longitude -180..180."
                )
            return {
                "name": query,
                "display_name": f"{latitude:.4f}, {longitude:.4f}",
                "latitude": latitude,
                "longitude": longitude,
                "timezone": "auto",
                "country": None,
                "admin1": None,
            }

        payload = self._get_json(
            GEOCODING_URL,
            {"name": query, "count": 1, "language": "en", "format": "json"},
        )
        results = payload.get("results") or []
        if not results:
            raise LocationNotFoundError(
                f"Could not resolve location '{query}'. Add a country, province, or state."
            )

        result = results[0]
        qualifiers = [result.get("admin1"), result.get("country")]
        display_name = ", ".join(
            [result["name"], *[value for value in qualifiers if value and value != result["name"]]]
        )
        return {
            "name": result["name"],
            "display_name": display_name,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "timezone": result.get("timezone", "auto"),
            "country": result.get("country"),
            "admin1": result.get("admin1"),
        }

    def current_weather(self, location: str) -> dict[str, Any]:
        """Return normalized current conditions for a location."""
        resolved = self.resolve_location(location)
        payload = self._get_json(
            FORECAST_URL,
            {
                "latitude": resolved["latitude"],
                "longitude": resolved["longitude"],
                "current": ",".join(
                    [
                        "temperature_2m",
                        "apparent_temperature",
                        "relative_humidity_2m",
                        "weather_code",
                        "precipitation",
                        "wind_speed_10m",
                        "wind_direction_10m",
                    ]
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
                "timezone": "auto",
            },
        )
        current = payload.get("current")
        if not isinstance(current, dict):
            raise WeatherAdapterError("Current conditions were missing from the weather response.")
        return {
            "location": resolved,
            "observed_at": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "relative_humidity_percent": current.get("relative_humidity_2m"),
            "condition": weather_description(current.get("weather_code")),
            "weather_code": current.get("weather_code"),
            "precipitation_mm": current.get("precipitation"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_direction_degrees": current.get("wind_direction_10m"),
            "timezone": payload.get("timezone"),
            "source": "Open-Meteo",
        }

    def forecast(self, location: str, days: int = 7) -> dict[str, Any]:
        """Return a normalized daily forecast for 1 through 16 days."""
        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= MAX_FORECAST_DAYS:
            raise InvalidWeatherRequestError(
                f"Forecast days must be an integer between 1 and {MAX_FORECAST_DAYS}."
            )
        resolved = self.resolve_location(location)
        payload = self._get_json(
            FORECAST_URL,
            {
                "latitude": resolved["latitude"],
                "longitude": resolved["longitude"],
                "daily": ",".join(
                    [
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "apparent_temperature_max",
                        "apparent_temperature_min",
                        "precipitation_probability_max",
                        "precipitation_sum",
                        "wind_speed_10m_max",
                    ]
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
                "forecast_days": days,
                "timezone": "auto",
            },
        )
        daily = payload.get("daily")
        if not isinstance(daily, dict) or not daily.get("time"):
            raise WeatherAdapterError("Daily forecast data was missing from the weather response.")

        def value(key: str, index: int) -> Any:
            values = daily.get(key) or []
            return values[index] if index < len(values) else None

        forecasts = []
        for index, forecast_date in enumerate(daily["time"]):
            code = value("weather_code", index)
            forecasts.append(
                {
                    "date": forecast_date,
                    "condition": weather_description(code),
                    "weather_code": code,
                    "temperature_max_c": value("temperature_2m_max", index),
                    "temperature_min_c": value("temperature_2m_min", index),
                    "feels_like_max_c": value("apparent_temperature_max", index),
                    "feels_like_min_c": value("apparent_temperature_min", index),
                    "precipitation_probability_max_percent": value(
                        "precipitation_probability_max", index
                    ),
                    "precipitation_sum_mm": value("precipitation_sum", index),
                    "wind_speed_max_kmh": value("wind_speed_10m_max", index),
                }
            )
        return {
            "location": resolved,
            "timezone": payload.get("timezone"),
            "days": forecasts,
            "source": "Open-Meteo",
        }

    def travel_recommendation(self, location: str, target_date: str) -> dict[str, Any]:
        """Build a documented recommendation from a forecast for an ISO date."""
        try:
            requested_date = date.fromisoformat(target_date)
        except ValueError as exc:
            raise InvalidWeatherRequestError("Date must use YYYY-MM-DD format.") from exc

        days_ahead = (requested_date - date.today()).days
        if not 0 <= days_ahead < MAX_FORECAST_DAYS:
            raise InvalidWeatherRequestError(
                f"Date must be today or within the next {MAX_FORECAST_DAYS - 1} days."
            )
        result = self.forecast(location, days_ahead + 1)
        day = next((item for item in result["days"] if item["date"] == target_date), None)
        if day is None:
            raise WeatherAdapterError("The requested date was absent from the forecast.")

        precipitation_probability = day["precipitation_probability_max_percent"] or 0
        low = day["temperature_min_c"]
        high = day["temperature_max_c"]
        max_wind = day["wind_speed_max_kmh"] or 0
        recommendations: list[str] = []
        reasons: list[str] = []

        if precipitation_probability >= 40:
            recommendations.append("Bring an umbrella or waterproof layer.")
            reasons.append(f"precipitation probability is {precipitation_probability}% (threshold: 40%)")
        if low is not None and low < 10:
            recommendations.append("Bring a warm jacket.")
            reasons.append(f"forecast low is {low}°C (jacket threshold: below 10°C)")
        elif high is not None and high < 18:
            recommendations.append("Bring a light jacket.")
            reasons.append(f"forecast high is {high}°C (light-jacket threshold: below 18°C)")
        if high is not None and high >= 28:
            recommendations.append("Plan for heat, hydration, and sun protection.")
            reasons.append(f"forecast high is {high}°C (heat threshold: 28°C)")
        if max_wind >= 40:
            recommendations.append("Expect strong winds and secure loose items.")
            reasons.append(f"maximum wind is {max_wind} km/h (threshold: 40 km/h)")
        if not recommendations:
            recommendations.append("No special rain, cold, heat, or wind precautions are indicated.")
            reasons.append("all forecast values are below the documented recommendation thresholds")

        return {
            "location": result["location"],
            "date": target_date,
            "forecast": day,
            "recommendations": recommendations,
            "reasoning": reasons,
            "thresholds": {
                "umbrella_precipitation_probability_percent": 40,
                "warm_jacket_below_c": 10,
                "light_jacket_high_below_c": 18,
                "heat_precautions_at_or_above_c": 28,
                "strong_wind_at_or_above_kmh": 40,
            },
            "source": "Open-Meteo",
        }
