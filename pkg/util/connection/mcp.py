import asyncio
from typing import Dict, Any, List
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPClient:
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url
        self.timeout = timeout
        self.client = Client(StreamableHttpTransport(url=base_url))
    async def list_tools(self) -> List[dict]:
        try:
            async with self.client:   # 🔥 REQUIRED SESSION
                tools = await self.client.list_tools()

                # Convert Tool objects → dict
                formatted = []
                for t in tools:
                    formatted.append({
                        "name": getattr(t, "name", None),
                        "description": getattr(t, "description", None),
                        "input_schema": getattr(t, "inputSchema", None),
                    })

                return formatted

        except Exception as e:
            print(f"[MCP ERROR] list_tools: {e}")
            return []

    async def execute_tool(self, name: str, params: Dict[str, Any]):
        try:
            async with self.client:   
                result = await self.client.call_tool(name=name, arguments=params)
                return result

        except Exception as e:
            return {"error": f"MCP execution failed: {str(e)}"}

    async def debug_tools(self):
        async with self.client:
            tools = await self.client.list_tools()
            print("RAW TOOLS:", tools)
            print("COUNT:", len(tools))