from __future__ import annotations

from datetime import date, timedelta

import httpx
import pytest

from weather_adapter import (
    InvalidWeatherRequestError,
    LocationNotFoundError,
    OpenMeteoAdapter,
    WeatherAdapterError,
    weather_description,
)


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def geocode_response():
    return {
        "results": [
            {
                "name": "Toronto",
                "latitude": 43.70011,
                "longitude": -79.4163,
                "country": "Canada",
                "admin1": "Ontario",
                "timezone": "America/Toronto",
            }
        ]
    }


def daily_response(days=2, rain_probability=55):
    start = date.today()
    dates = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    return {
        "timezone": "America/Toronto",
        "daily": {
            "time": dates,
            "weather_code": [61] * days,
            "temperature_2m_max": [17.0] * days,
            "temperature_2m_min": [8.0] * days,
            "apparent_temperature_max": [16.0] * days,
            "apparent_temperature_min": [7.0] * days,
            "precipitation_probability_max": [rain_probability] * days,
            "precipitation_sum": [2.5] * days,
            "wind_speed_10m_max": [22.0] * days,
        },
    }


def test_resolve_city_and_current_weather():
    def handler(request):
        if "geocoding" in str(request.url):
            return httpx.Response(200, json=geocode_response())
        return httpx.Response(
            200,
            json={
                "timezone": "America/Toronto",
                "current": {
                    "time": "2026-08-08T10:00",
                    "temperature_2m": 23.2,
                    "apparent_temperature": 24.1,
                    "relative_humidity_2m": 62,
                    "weather_code": 2,
                    "precipitation": 0.0,
                    "wind_speed_10m": 12.4,
                    "wind_direction_10m": 240,
                },
            },
        )

    adapter = OpenMeteoAdapter(make_client(handler))
    result = adapter.current_weather("Toronto, Ontario")
    assert result["location"]["display_name"] == "Toronto, Ontario, Canada"
    assert result["condition"] == "Partly cloudy"
    assert result["relative_humidity_percent"] == 62


def test_coordinates_bypass_geocoding():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=daily_response(1))

    adapter = OpenMeteoAdapter(make_client(handler))
    result = adapter.forecast("43.7,-79.4", 1)
    assert len(calls) == 1
    assert result["location"]["latitude"] == 43.7


def test_forecast_normalizes_daily_arrays():
    def handler(request):
        if "geocoding" in str(request.url):
            return httpx.Response(200, json=geocode_response())
        return httpx.Response(200, json=daily_response(2))

    result = OpenMeteoAdapter(make_client(handler)).forecast("Toronto", 2)
    assert len(result["days"]) == 2
    assert result["days"][0]["condition"] == "Slight rain"
    assert result["days"][0]["precipitation_probability_max_percent"] == 55


def test_recommendation_explains_thresholds():
    def handler(request):
        if "geocoding" in str(request.url):
            return httpx.Response(200, json=geocode_response())
        return httpx.Response(200, json=daily_response(1, 55))

    target = date.today().isoformat()
    result = OpenMeteoAdapter(make_client(handler)).travel_recommendation("Toronto", target)
    assert "Bring an umbrella or waterproof layer." in result["recommendations"]
    assert "Bring a warm jacket." in result["recommendations"]
    assert result["thresholds"]["umbrella_precipitation_probability_percent"] == 40


@pytest.mark.parametrize("days", [0, 17, True, 1.5])
def test_invalid_forecast_days(days):
    with pytest.raises(InvalidWeatherRequestError):
        OpenMeteoAdapter(make_client(lambda _: None)).forecast("Toronto", days)


def test_bad_coordinates_fail_cleanly():
    with pytest.raises(InvalidWeatherRequestError, match="latitude"):
        OpenMeteoAdapter(make_client(lambda _: None)).resolve_location("91,181")


def test_location_not_found():
    client = make_client(lambda _: httpx.Response(200, json={"generationtime_ms": 0.1}))
    with pytest.raises(LocationNotFoundError, match="Could not resolve"):
        OpenMeteoAdapter(client).resolve_location("not-a-real-location")


def test_timeout_has_clean_error():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(WeatherAdapterError, match="timed out"):
        OpenMeteoAdapter(make_client(handler)).resolve_location("Toronto")


def test_unknown_wmo_code_is_explicit():
    assert weather_description(123) == "Unknown weather code (123)"

