# Weather-Prediction MCP Server Submission

## Links

- Repository: <https://github.com/rajeshd101/databricks-mcp-demo>
- Databricks App: <https://weather-prediction-mcp-rajesh-1352785079224954.aws.databricksapps.com>
- MCP endpoint: `https://weather-prediction-mcp-rajesh-1352785079224954.aws.databricksapps.com/mcp`

The App URL requires Databricks workspace authentication.

## Implementation

- API: Open-Meteo; no API key or secret required.
- MCP framework: FastMCP with Streamable HTTP at `/mcp`.
- Adapter: `weather_adapter.py` owns geocoding, weather HTTP calls, parsing, normalization, WMO descriptions, and recommendation logic.
- Server: `weather_mcp_server.py` exposes three thin `@mcp.tool` functions.
- Agent configuration: `agent/system_prompt.md` and `agent/agent_config.yaml`.

## Tools

1. `get_current_weather(location)`
2. `get_forecast(location, days)`
3. `get_travel_recommendation(location, date)`

The recommendation tool applies documented umbrella, jacket, heat, and wind thresholds and returns both its recommendations and reasoning.

## Verification

- Automated tests: 16 passed.
- Combined adapter/server statement coverage: 77%.
- Live Open-Meteo calls: passed for all three capabilities.
- Databricks deployment: succeeded.
- Latest deployment ID: `01f19380a61a124c82a5ce76e3042578`.
- Authenticated deployed MCP initialization: HTTP 200.
- MCP protocol version: `2025-06-18`.
- Deployed tool discovery: all three tools found.
- Deployed tool invocation: all three tools returned `protocol_error=False` and `tool_ok=True`.
- Secret scan: no committed API keys or tokens.

## Evidence

- `evidence/databricks-app-overview.png`: deployed Databricks App screenshot.
- `evidence/deployment.md`: deployment and protocol verification.
- `evidence/demo_results.md`: three live natural-language example questions with tool calls and results.
- `evidence/agent_bricks_transcript.md`: Agent Bricks conversations, registered MCP tool traces, final answers, and ambiguity guardrail evidence.
- `evidence/Mcp_tools_screenshot.jpg`: active governed MCP Service with all three tools.
- `evidence/MCP_conversation_1.jpg`: Supervisor Agent configuration, attached MCP Service, system instructions, current-weather tool trace, and grounded response.
- `evidence/Mcp_conversation_3.jpg`: Chicago forecast plus Austin recommendation and forecast tool traces with final-answer evidence.
- `TESTING.md`: reproducible local and deployed testing commands.

## Acceptance checklist

- [x] FastMCP server using Streamable HTTP.
- [x] Three required tools with typed signatures and Args/Returns docstrings.
- [x] Separate HTTP/parsing adapter module.
- [x] Derived recommendation logic with documented thresholds.
- [x] Clean errors for invalid input and upstream failures.
- [x] No API keys required or secrets committed.
- [x] `requirements.txt` and `app.yaml` included.
- [x] MCP server deployed as its own Databricks App.
- [x] Agent system prompt and tool configuration included.
- [x] Agent Bricks supervisor connected to the registered student MCP Service.
- [x] Agent behavior demonstrated with tool traces and grounded final answers.
- [x] README contains architecture, setup, tools, testing, and limitations.
- [x] Three live MCP tool demonstrations included.
- [x] GitHub repository and Databricks App links included.
- [x] Three Agent Bricks weather conversations recorded as copied transcripts.
- [x] Ambiguous-location guardrail conversation recorded.
- [x] Agent Bricks MCP registration and conversation screenshots included.

## Agent Bricks registration

The deployed MCP is registered as `bootcamp_students.rajesh.weather_prediction_mcp` and connected to `supervisor-agent-2026-08-08-20-02-56`. Copied conversation evidence demonstrates all three tools and the ambiguous-location guardrail. The Chicago transcript includes a relative-date label mismatch; it is retained verbatim and explicitly identified in the evidence file rather than silently corrected.
