
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def list_mcp_tools():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()

            print("Connected to Alexa++ MCP server!")
            print("\nAvailable tools:")

            for tool in result.tools:
                print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(list_mcp_tools())
