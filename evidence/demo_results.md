# Live Weather Tool Demonstration

Generated: 2026-08-08

## What is the current weather in Toronto?

Tool call: `get_current_weather({"location": "Toronto, Ontario, Canada"})`

```json
{
  "location": {
    "name": "Toronto",
    "display_name": "Toronto, Ontario, Canada",
    "latitude": 43.70643,
    "longitude": -79.39864,
    "timezone": "America/Toronto",
    "country": "Canada",
    "admin1": "Ontario"
  },
  "observed_at": "2026-08-08T18:00",
  "temperature_c": 23.8,
  "feels_like_c": 26.8,
  "relative_humidity_percent": 89,
  "condition": "Overcast",
  "weather_code": 3,
  "precipitation_mm": 0.0,
  "wind_speed_kmh": 12.4,
  "wind_direction_degrees": 210,
  "timezone": "America/Toronto",
  "source": "Open-Meteo"
}
```

## Will it rain in Chicago tomorrow?

Tool call: `get_forecast({"location": "Chicago, Illinois, USA", "days": 2})`

```json
{
  "location": {
    "name": "Chicago",
    "display_name": "Chicago, Illinois, United States",
    "latitude": 41.85003,
    "longitude": -87.65005,
    "timezone": "America/Chicago",
    "country": "United States",
    "admin1": "Illinois"
  },
  "timezone": "America/Chicago",
  "days": [
    {
      "date": "2026-08-08",
      "condition": "Mainly clear",
      "weather_code": 1,
      "temperature_max_c": 27.0,
      "temperature_min_c": 20.5,
      "feels_like_max_c": 32.4,
      "feels_like_min_c": 22.8,
      "precipitation_probability_max_percent": 6,
      "precipitation_sum_mm": 0.0,
      "wind_speed_max_kmh": 16.2
    },
    {
      "date": "2026-08-09",
      "condition": "Light drizzle",
      "weather_code": 51,
      "temperature_max_c": 32.5,
      "temperature_min_c": 18.0,
      "feels_like_max_c": 34.6,
      "feels_like_min_c": 19.1,
      "precipitation_probability_max_percent": 29,
      "precipitation_sum_mm": 0.4,
      "wind_speed_max_kmh": 24.4
    }
  ],
  "source": "Open-Meteo"
}
```

## Should I bring a jacket or umbrella to Austin tomorrow?

Tool call: `get_travel_recommendation({"location": "Austin, Texas, USA", "date": "2026-08-09"})`

```json
{
  "location": {
    "name": "Austin",
    "display_name": "Austin, Texas, United States",
    "latitude": 30.26715,
    "longitude": -97.74306,
    "timezone": "America/Chicago",
    "country": "United States",
    "admin1": "Texas"
  },
  "date": "2026-08-09",
  "forecast": {
    "date": "2026-08-09",
    "condition": "Partly cloudy",
    "weather_code": 2,
    "temperature_max_c": 36.8,
    "temperature_min_c": 25.4,
    "feels_like_max_c": 39.3,
    "feels_like_min_c": 30.3,
    "precipitation_probability_max_percent": 3,
    "precipitation_sum_mm": 0.0,
    "wind_speed_max_kmh": 21.0
  },
  "recommendations": [
    "Plan for heat, hydration, and sun protection."
  ],
  "reasoning": [
    "forecast high is 36.8°C (heat threshold: 28°C)"
  ],
  "thresholds": {
    "umbrella_precipitation_probability_percent": 40,
    "warm_jacket_below_c": 10,
    "light_jacket_high_below_c": 18,
    "heat_precautions_at_or_above_c": 28,
    "strong_wind_at_or_above_kmh": 40
  },
  "source": "Open-Meteo"
}
```

> These are live API tool results, not screenshots of Agent Bricks. Add Agent Bricks screenshots after deployment.
