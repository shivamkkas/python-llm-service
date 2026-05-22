from typing import *
from pkg.util import connection

class MCPManager:

    def __init__(self, client: connection.MCPClient):
        self.client = client
        self._tool_cache = None   # cache tools (important)

    async def Get_tools_schema(self):
        if self._tool_cache is None:
            self._tool_cache = await self.client.list_tools()
        return self._tool_cache

    async def execute(self, name: str, params: Dict[str, Any]):
        return await self.client.execute_tool(name, params)