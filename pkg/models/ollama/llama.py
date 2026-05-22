import asyncio
import json
import logging
import re
from datetime import datetime
from typing import List, Optional, Dict, Any

import requests

from pkg.cache import MCPManager
from pkg import config


class NewOllamaModel:
    def __init__(self, cfg: config.Config, mcp: MCPManager):
        self._provider = cfg.app.models.ollama
        self._tools = mcp
        self._log = logging.getLogger(__name__)

    # -------------------------------
    # 📌 Get available models
    # -------------------------------
    def get_available_models(self) -> List[str]:
        if not self._provider.enable:
            return []

        try:
            res = requests.get(
                f"{self._provider.base_url}/api/tags",
                timeout=5
            )
            res.raise_for_status()

            data = res.json()
            return [m.get("name") for m in data.get("models", [])]

        except Exception as e:
            self._log.error(f"Ollama model fetch error: {e}")
            return []

    # -------------------------------
    # 📌 Main response function
    # -------------------------------
    def get_response(self, query: str, model: str) -> str:
        try:
            tools = asyncio.run(self._tools.Get_tools_schema())
        except Exception as e:
            self._log.error(f"Tool schema error: {e}")
            tools = []

        prompt = self._build_prompt(query, tools)

        response_text = self._call_ollama(model, prompt)

        tool_call = self._extract_tool_call(response_text)

        # 👉 If no tool needed → return LLM response
        if not tool_call:
            return response_text

        # 👉 Execute tool
        try:
            tool_result = asyncio.run(
                self._tools.execute(
                    tool_call["name"],
                    tool_call["input"]
                )
            )
        except Exception as e:
            self._log.error(f"Tool execution error: {e}")
            return "Error executing tool."

        self._log.info(f"Tool executed: {tool_call['name']}")

        # 👉 Final response with tool output
        final_prompt = self._build_final_prompt(query, tool_result)

        return self._call_ollama(model, final_prompt)

    # -------------------------------
    # 📌 Call Ollama API
    # -------------------------------
    def _call_ollama(self, model: str, prompt: str) -> str:
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }

            res = requests.post(
                f"{self._provider.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            res.raise_for_status()

            return res.json().get("response", "")

        except Exception as e:
            self._log.error(f"Ollama API error: {e}")
            return "Error generating response."

    # -------------------------------
    # 📌 Build initial prompt
    # -------------------------------
    def _build_prompt(self, query: str, tools) -> str:
        tool_desc = json.dumps(tools, indent=2)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""
    You are an AI assistant.

    Current datetime: {now}

    You can use tools if required.

    CRITICAL RULES:
    - ALWAYS follow tool schema EXACTLY
    - ALWAYS wrap input inside "payload"
    - NEVER skip required fields
    - Convert relative time (last week, yesterday, etc.) into exact datetime

    Example Tool Call:
    {{
    "tool": "get_asset_alarm",
    "input": {{
        "payload": {{
        "asset_code": "TC001",
        "organization_code": "ORG1",
        "start_ts": "2026-04-10 00:00:00",
        "end_ts": "2026-04-17 23:59:59"
        }}
    }}
    }}

    Available tools:
    {tool_desc}

    If tool is needed → return ONLY JSON  
    Otherwise → normal text

    User Query:
    {query}
    """
    # -------------------------------
    # 📌 Extract tool call safely
    # -------------------------------
    def _extract_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            # Extract JSON block
            matches = re.findall(r'\{.*?\}', text, re.DOTALL)

            for match in matches:
                cleaned = re.sub(r'//.*', '', match).strip()

                try:
                    data = json.loads(cleaned)

                    if "tool" in data:
                        return {
                            "name": data["tool"],
                            "input": data.get("input", {})
                        }

                except json.JSONDecodeError:
                    continue

        except Exception as e:
            self._log.error(f"Tool parse error: {e}")
            self._log.debug(f"RAW TEXT: {text}")

        return None