from pkg.cache import APIKeyManager,MCPManager
from pkg import constant,config
from typing import List
import requests


class NewClaudeAiModel(APIKeyManager):

    def __init__(self,config:config.Models,mcp:MCPManager):
        super().__init__()  
        self.config = config
        self.tools = mcp

    def GetAvailableModels(self) -> List[str]:
        return constant.ModelRegistry.CLAUDE_MODELS
    def GetResponse(self, query: str, model: str) -> str:
        if not self.config.anthropic.enabled:
            return
        api_key = self.get_key(constant.Models.CLAUDE)

        if not api_key:
            raise Exception("Claude API key not set")

        headers = {"x-api-key": api_key,"anthropic-version": "2023-06-01","content-type": "application/json"}
        messages = [{"role": "user","content": query}]
        payload = {"model": model,"max_tokens": 1000,"messages": messages}
        if self.tools:
            payload["tools"] = self.tools.get_tools_schema()

        response = requests.post(self.config.ClaudeUrl, headers=headers, json=payload)
        data = response.json()

        tool_call = self._extract_tool_call(data)

        if not tool_call:
            return data["content"][0]["text"]


        tool_result = self.tools.execute(
            tool_call["name"],
            tool_call["input"]
        )

        messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "tool_result",
                    "content": str(tool_result)
                }
            ]
        })

        payload["messages"] = messages

        final_response = requests.post(
            self.config.anthropic.base_url,
            headers=headers,
            json=payload
        )
        final_data = final_response.json()
        return final_data["content"][0]["text"]
    def _extract_tool_call(self, data):
        for item in data.get("content", []):
            if item.get("type") == "tool_use":
                return {
                    "name": item["name"],
                    "input": item["input"]
                }
        return None