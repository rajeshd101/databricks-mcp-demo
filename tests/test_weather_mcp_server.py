from unittest.mock import patch

from weather_adapter import LocationNotFoundError
from weather_mcp_server import get_current_weather, get_forecast, get_travel_recommendation


class FakeAdapter:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def current_weather(self, location):
        return {"location": location, "temperature_c": 20}

    def forecast(self, location, days):
        return {"location": location, "days_requested": days}

    def travel_recommendation(self, location, target_date):
        return {"location": location, "date": target_date, "recommendations": ["Umbrella"]}


def call_tool(tool, *args):
    function = getattr(tool, "fn", tool)
    return function(*args)


@patch("weather_mcp_server.OpenMeteoAdapter", FakeAdapter)
def test_tools_wrap_success_results():
    assert call_tool(get_current_weather, "Toronto")["ok"] is True
    assert call_tool(get_forecast, "Toronto", 3)["data"]["days_requested"] == 3
    assert call_tool(get_travel_recommendation, "Toronto", "2026-08-08")["ok"] is True


class MissingLocationAdapter(FakeAdapter):
    def current_weather(self, location):
        raise LocationNotFoundError("Please clarify the location.")


@patch("weather_mcp_server.OpenMeteoAdapter", MissingLocationAdapter)
def test_tool_returns_clean_expected_error():
    result = call_tool(get_current_weather, "Springfield")
    assert result == {"ok": False, "error": "Please clarify the location."}


class ExplodingAdapter(FakeAdapter):
    def forecast(self, location, days):
        raise RuntimeError("sensitive internal detail")


@patch("weather_mcp_server.OpenMeteoAdapter", ExplodingAdapter)
def test_tool_hides_unexpected_internal_error():
    result = call_tool(get_forecast, "Toronto", 3)
    assert result["ok"] is False
    assert "sensitive" not in result["error"]

