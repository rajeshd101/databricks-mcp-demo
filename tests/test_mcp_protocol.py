import asyncio

from fastmcp import Client

from weather_mcp_server import mcp


def test_mcp_protocol_discovers_required_tools():
    async def check():
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools} == {
                "get_current_weather",
                "get_forecast",
                "get_travel_recommendation",
            }

    asyncio.run(check())

