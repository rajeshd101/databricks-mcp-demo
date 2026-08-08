# Databricks Deployment Evidence

- Workspace user: `drajesh@hotmail.com`
- App name: `weather-prediction-mcp-rajesh`
- App URL: `https://weather-prediction-mcp-rajesh-1352785079224954.aws.databricksapps.com`
- MCP URL: `https://weather-prediction-mcp-rajesh-1352785079224954.aws.databricksapps.com/mcp`
- Deployment ID: `01f193759acb112ca8e75736dc9ef2f8`
- Deployment state: `SUCCEEDED`
- Deployment message: `App started successfully`
- Verified: `2026-08-08T22:08:26Z`

Authenticated Streamable HTTP initialization returned:

```text
HTTP/2 200
content-type: text/event-stream
protocolVersion: 2025-06-18
serverInfo.name: Weather Prediction MCP
serverInfo.version: 3.4.6
```

The response advertised MCP tool capability. A local Streamable HTTP protocol test also discovered and called:

- `get_current_weather`
- `get_forecast`
- `get_travel_recommendation`

## Agent Bricks registration status

The current workspace UI uses governed Unity Catalog MCP Services. Databricks documentation currently states that registering Databricks Apps as an MCP Service is not supported during the Beta. The assignment's older direct external-MCP registration flow is therefore unavailable in this workspace. The app itself is deployed and MCP-protocol verified; no short-lived bearer token was saved as a permanent solution.
