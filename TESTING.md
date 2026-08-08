# Testing Guide

## Automated tests

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
```

Expected result: `16 passed`.

Coverage command:

```bash
.venv/bin/pytest --cov=weather_adapter --cov=weather_mcp_server --cov-report=term-missing
```

Latest result: 77% combined statement coverage.

## Live Open-Meteo demonstration

```bash
PYTHONPATH=. .venv/bin/python scripts/run_demo.py
```

This calls current conditions, forecast, and recommendation capabilities against Open-Meteo and writes [`evidence/demo_results.md`](evidence/demo_results.md).

## Local MCP protocol test

Start the server:

```bash
.venv/bin/python weather_mcp_server.py
```

In a second terminal:

```bash
.venv/bin/python - <<'PY'
import asyncio
import json
from fastmcp import Client

async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        tools = await client.list_tools()
        print([tool.name for tool in tools])
        result = await client.call_tool(
            "get_current_weather",
            {"location": "Toronto, Ontario, Canada"},
        )
        payload = json.loads(result.content[0].text)
        assert not result.is_error
        assert payload["ok"] is True
        print(json.dumps(payload, indent=2))

asyncio.run(main())
PY
```

Expected tools:

- `get_current_weather`
- `get_forecast`
- `get_travel_recommendation`

## Deployed Databricks MCP test

Authenticate the CLI:

```bash
databricks auth login --profile dbc-7b106152-caf3 \
  --host https://dbc-7b106152-caf3.cloud.databricks.com
```

Test discovery and all three tools without printing the OAuth token:

```bash
DBX_MCP_TOKEN=$(
  databricks auth token -p dbc-7b106152-caf3 -o json |
  python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])'
) .venv/bin/python - <<'PY'
import asyncio
import json
import os
from datetime import date, timedelta
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

URL = "https://weather-prediction-mcp-rajesh-1352785079224954.aws.databricksapps.com/mcp"

async def main():
    transport = StreamableHttpTransport(
        URL,
        headers={"Authorization": f"Bearer {os.environ['DBX_MCP_TOKEN']}"},
    )
    async with Client(transport) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools]
        print("Discovered:", names)
        assert set(names) == {
            "get_current_weather",
            "get_forecast",
            "get_travel_recommendation",
        }
        calls = [
            ("get_current_weather", {"location": "Toronto, Ontario, Canada"}),
            ("get_forecast", {"location": "Chicago, Illinois, USA", "days": 2}),
            (
                "get_travel_recommendation",
                {
                    "location": "Austin, Texas, USA",
                    "date": (date.today() + timedelta(days=1)).isoformat(),
                },
            ),
        ]
        for name, arguments in calls:
            result = await client.call_tool(name, arguments)
            payload = json.loads(result.content[0].text)
            assert not result.is_error
            assert payload["ok"] is True
            print(f"{name}: passed")

asyncio.run(main())
PY
```

## Negative tests

Expected clean failures:

- Unknown location returns `ok: false` with a clarification message.
- `days=0` or `days=17` returns the supported 1-16 range.
- A malformed date returns the required `YYYY-MM-DD` format.
- API failures return a clean error without a stack trace.

