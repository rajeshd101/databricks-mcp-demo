# Weather-Prediction MCP Server + Agent Requirements

## Objective

Build and deploy a weather-forecast MCP server and connect it to a Databricks Agent Bricks agent. The agent must answer natural-language weather questions and provide simple forecast-based recommendations.

## Architecture

- Deploy the MCP server as its own Databricks App.
- Register the deployed MCP server as an external MCP tool for a Databricks Agent Bricks agent.
- Use FastMCP, or another MCP-compliant framework, with streamable HTTP transport.
- Keep MCP tool functions thin.
- Put all weather API requests and response parsing in a separate adapter module.
- A dashboard showing recent queries or predictions is optional extra credit.

## Weather API

Use a free weather API that does not require a paid tier or credit card. Recommended options:

- Open-Meteo: preferred; no signup or API key required.
- National Weather Service API: no key required; United States only.
- WeatherAPI.com: free API key required.

If the selected API requires credentials:

- Store them in Databricks Secrets.
- Retrieve them through `WorkspaceClient().secrets.get_secret()` or an equivalent helper.
- Never hardcode or commit credentials.

## Required MCP Tools

Expose at least three tools with clear names, typed parameters, and Args/Returns docstrings.

### 1. Current conditions

Accept a supported location format and return:

- Temperature
- Weather conditions
- Humidity
- Wind information

Example: `get_current_weather(location)`

### 2. Multi-day forecast

Accept a location and number of days and return, for each day:

- High temperature
- Low temperature
- Precipitation probability
- Weather conditions

Example: `get_forecast(location, days)`

### 3. Prediction or recommendation

Apply documented logic to forecast data and explain the resulting judgment. It must do more than return raw API data.

Examples:

- `predict_umbrella_needed(location, date)`
- `get_travel_recommendation(location, date)`
- Recommend an umbrella when precipitation probability exceeds a documented threshold such as 40%.

## Error Handling and Guardrails

- Return clean, structured errors for invalid or ambiguous locations.
- Return clean errors for upstream API failures; do not expose stack traces.
- The agent must ask for clarification when it cannot resolve a location.
- The agent must report tool or API failures instead of guessing.
- The agent must not invent weather observations or forecasts.

## Agent Configuration

Provide a clear system prompt that defines:

- The agent's weather-assistant role.
- Which tools it should call and in what order.
- Location-resolution behavior.
- Failure behavior.
- No-hallucination guardrails.

Include the system prompt and registered tool list in the repository.

## Required Files

- MCP server module
- Weather API adapter module
- `requirements.txt`
- `app.yaml`
- Agent system prompt and tool configuration
- `README.md`

## README Content

Document:

- Architecture
- Weather API and authentication method
- Available tools and their parameters
- Local setup and testing
- Databricks App deployment
- External MCP registration
- Agent Bricks setup
- Known limitations

An architecture diagram is encouraged but optional.

## Demonstration

Provide evidence of at least three different natural-language agent interactions, including tool calls and final answers. Example questions:

- Will it rain in Chicago tomorrow?
- Should I bring a jacket to Austin this weekend?
- What is the five-day forecast for Toronto?

Evidence may be pasted into the README or supplied as screenshots.

## Optional Extra Credit

- Severe-weather alerts
- Historical-weather lookup
- Multi-city weather comparison
- Dashboard for recent agent queries and predictions

## Submission

- Push the MCP server and agent configuration to a personal repository or branch.
- Include the README.
- Share the repository or branch link.
- Share Databricks App URLs, or screenshots when workspace access cannot be shared.
- Accepted uploaded file types: `.zip`, `.png`, `.jpg`, `.jpeg`, and `.pdf`.

## Acceptance Checklist

- [ ] MCP server uses an MCP-compliant framework and streamable HTTP.
- [ ] At least three required weather tools are exposed with `@mcp.tool` decorators.
- [ ] Tool functions include clear Args/Returns docstrings.
- [ ] HTTP and parsing logic are isolated in an adapter module.
- [ ] Prediction logic applies and documents a meaningful threshold or rule.
- [ ] Invalid inputs and API failures produce clean errors.
- [ ] No secrets or API keys are hardcoded or committed.
- [ ] `requirements.txt` and `app.yaml` are present.
- [ ] MCP server is deployed as a Databricks App.
- [ ] Agent Bricks is connected to the server as an external MCP.
- [ ] Agent system prompt includes tool-use and no-guessing guardrails.
- [ ] README contains setup, architecture, tools, and API details.
- [ ] At least three agent demonstrations are included.
