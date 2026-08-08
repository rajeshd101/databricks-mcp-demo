# Weather-Prediction MCP Server + Agent

A Streamable HTTP MCP server backed by Open-Meteo, plus the prompt and registration metadata for a Databricks Agent Bricks weather agent. Open-Meteo requires no signup, API key, or committed secret.

## Architecture

```text
User
  |
  v
Databricks Agent Bricks
  |  external MCP / Streamable HTTP
  v
Databricks App: weather_mcp_server.py
  |
  v
weather_adapter.py
  |----------------------|
  v                      v
Open-Meteo Geocoding     Open-Meteo Forecast
```

The server functions only validate tool inputs and shape success/error envelopes. `weather_adapter.py` owns all HTTP calls, API parsing, WMO-code translation, and recommendation logic.

## Tools

| Tool | Inputs | Result |
|---|---|---|
| `get_current_weather` | `location` | Temperature, feels-like temperature, condition, humidity, precipitation, and wind |
| `get_forecast` | `location`, `days` (1-16) | Daily high/low, feels-like values, condition, precipitation probability/amount, and wind |
| `get_travel_recommendation` | `location`, `date` (`YYYY-MM-DD`) | Forecast-backed umbrella, jacket, heat, and wind recommendations with explicit thresholds |

Locations may be a city/postal-code query or a `latitude,longitude` pair. All temperatures use Celsius, wind uses km/h, and precipitation uses millimetres.

Recommendation thresholds:

- Umbrella or waterproof layer: precipitation probability at least 40%.
- Warm jacket: daily low below 10°C.
- Light jacket: daily high below 18°C when the warm-jacket rule does not apply.
- Heat precautions: daily high at least 28°C.
- Strong-wind precautions: maximum daily wind at least 40 km/h.

## Local setup

Python 3.10 or newer is required.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
```

Start the server:

```bash
.venv/bin/python weather_mcp_server.py
```

The Streamable HTTP endpoint is `http://localhost:8000/mcp`.

Generate three live Open-Meteo examples:

```bash
PYTHONPATH=. .venv/bin/python scripts/run_demo.py
```

Results are written to [`evidence/demo_results.md`](evidence/demo_results.md). They prove live adapter calls, not an Agent Bricks deployment.

## Databricks App deployment

The MCP server is designed to run as one Databricks App. Authenticate the Databricks CLI first:

```bash
databricks auth login --host https://<workspace-host>
databricks auth profiles
```

Create a workspace source directory, upload the project, create the app, and deploy it:

```bash
export DBX_USER='<your-workspace-email>'
export APP_NAME='weather-prediction-mcp'
export SOURCE_PATH="/Workspace/Users/${DBX_USER}/${APP_NAME}"

databricks workspace mkdirs "$SOURCE_PATH"
databricks sync . "$SOURCE_PATH" --watch=false
databricks apps create "$APP_NAME" --description 'Open-Meteo weather MCP server'
databricks apps deploy "$APP_NAME" --source-code-path "$SOURCE_PATH"
databricks apps get "$APP_NAME" -o json
```

Do not upload `.venv`; it is excluded by `.gitignore`. Databricks Apps installs `requirements.txt` and starts the `app.yaml` command. The deployed external MCP URL is:

```text
https://weather-prediction-mcp-rajesh-1352785079224954.aws.databricksapps.com/mcp
```

The app endpoint is permission-controlled by Databricks Apps. Grant the intended agent/user permission to use the app before testing the MCP connection.

## Agent Bricks configuration

1. Open the deployed MCP App and copy its HTTPS URL.
2. In the Databricks workspace, register that URL plus `/mcp` as an external MCP using Streamable HTTP.
3. Verify tool discovery lists exactly:
   - `get_current_weather`
   - `get_forecast`
   - `get_travel_recommendation`
4. Create a new Agent Bricks agent.
5. Add the external MCP to the agent and enable the three tools.
6. Paste [`agent/system_prompt.md`](agent/system_prompt.md) into the system instructions.
7. Use [`agent/agent_config.yaml`](agent/agent_config.yaml) as the submitted tool-registration record; replace the endpoint placeholder with the deployed URL.
8. Test the three questions below and capture the tool call plus final response:
   - What is the current weather in Toronto?
   - Will it rain in Chicago tomorrow?
   - Should I bring a jacket or umbrella to Austin tomorrow?

## Error behavior

- Empty, unresolved, and invalid-coordinate locations return a clean `ok: false` response.
- Forecast lengths outside 1-16 and unsupported dates return validation messages.
- API timeouts, HTTP errors, malformed payloads, and unexpected internal failures do not expose stack traces.
- The agent prompt prohibits filling missing tool results with guesses.

## Verification status

- Automated adapter and MCP wrapper tests: see `tests/`.
- Live Open-Meteo adapter demonstration: see `evidence/demo_results.md`.
- Databricks App deployment: succeeded as `weather-prediction-mcp-rajesh`.
- Authenticated deployed MCP initialization: HTTP 200, MCP protocol `2025-06-18`.
- Deployed app screenshot: see `evidence/databricks-app-overview.png`.
- Agent Bricks registration: blocked by the current Databricks MCP Service limitation that Apps cannot be registered as an MCP Service. The assignment's referenced UI flow no longer matches the current workspace UI. Do not use a short-lived user bearer token as a permanent connection credential.

## Files

```text
agent/agent_config.yaml     External MCP tool record
agent/system_prompt.md      Agent Bricks instructions and guardrails
app.yaml                   Databricks App process configuration
evidence/demo_results.md   Three live API demonstrations
scripts/run_demo.py        Reproducible live demonstration
tests/                     Adapter and MCP error-boundary tests
weather_adapter.py         Open-Meteo HTTP/parsing/recommendation layer
weather_mcp_server.py      Thin FastMCP tool layer
```

## Limitations

- Current conditions are modeled Open-Meteo data, not direct observations from a local weather station.
- Geocoding selects the first Open-Meteo match; users should add province/state and country for ambiguous names.
- This version does not provide official severe-weather alerts. Users should consult official local alert services for safety-critical decisions.
- Forecasts are limited to Open-Meteo's next 16 days.
