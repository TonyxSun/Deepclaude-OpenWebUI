"""
title: DeepClaude
author: tonyxsun
description: A pipe that connects to the DeepClaude managed API, providing enhanced responses by combining DeepSeek's reasoning capabilities with Claude's response generation. Supports streaming for real-time responses.
version: 1.0.0
licence: MIT
"""

import json
import httpx
from typing import AsyncGenerator, Callable, Awaitable
from pydantic import BaseModel, Field

DATA_PREFIX = "data: "


def format_error(status_code, error) -> str:
    """Format error messages for consistent output."""
    try:
        err_msg = json.loads(error).get("message", error.decode(errors="ignore"))[:200]
    except Exception:
        err_msg = error.decode(errors="ignore")[:200]
    return json.dumps({"error": f"HTTP {status_code}: {err_msg}"}, ensure_ascii=False)


async def deepclaude_api_call(
    payload: dict, api_base_url: str, deepseek_api_key: str, anthropic_api_key: str
) -> AsyncGenerator[dict, None]:
    """Make a streaming API call to the DeepClaude managed API."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-DeepSeek-API-Token": deepseek_api_key,
        "X-Anthropic-API-Token": anthropic_api_key,
    }

    async with httpx.AsyncClient(http2=True) as client:
        try:
            async with client.stream(
                "POST",
                api_base_url,
                json=payload,
                headers=headers,
                timeout=300,
            ) as response:
                if response.status_code != 200:
                    error = await response.aread()
                    yield {"error": format_error(response.status_code, error)}
                    return

                # Process SSE stream
                buffer = ""
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    # Handle SSE format - event: content\ndata: {...}
                    if line.startswith("event:"):
                        continue
                    
                    if line.startswith(DATA_PREFIX):
                        json_str = line[len(DATA_PREFIX):]
                        try:
                            data = json.loads(json_str)
                            event_type = data.get("type")
                            
                            if event_type == "content":
                                # Process content events
                                for content_item in data.get("content", []):
                                    if content_item.get("type") == "text":
                                        text = content_item.get("text", "")
                                        yield {"choices": [{"delta": {"content": text}}]}
                                    elif content_item.get("type") == "text_delta":
                                        text = content_item.get("text", "")
                                        yield {"choices": [{"delta": {"content": text}}]}
                            
                            elif event_type == "done":
                                yield {"choices": [{"finish_reason": "stop"}]}
                                
                        except json.JSONDecodeError as e:
                            error_detail = f"ERROR - Content: {json_str}, Reason: {e}"
                            yield {"error": format_error("JSONDecodeError", error_detail)}
                            return

        except Exception as e:
            yield {"error": format_error("ConnectionError", str(e))}


class Pipe:
    class Valves(BaseModel):
        DEEPCLAUDE_API_BASE_URL: str = Field(
            default="https://api.deepclaude.com",
            description="DeepClaude API base URL",
        )
        DEEPSEEK_API_KEY: str = Field(
            default="",
            description="DeepSeek API authentication token",
            json_schema_extra={"format": "password"},
        )
        ANTHROPIC_API_KEY: str = Field(
            default="",
            description="Anthropic API authentication token",
            json_schema_extra={"format": "password"},
        )
        STREAM: bool = Field(
            default=True,
            description="Whether to stream the response",
        )
        VERBOSE: bool = Field(
            default=False,
            description="Whether to include detailed API responses in the output",
        )
        TEMPERATURE: float = Field(
            default=0.7,
            description="Temperature parameter for both models",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.data_prefix = DATA_PREFIX
        self.emitter = None

    def pipes(self):
        return [{"id": "DeepClaude", "name": "DeepClaude API"}]

    async def _emit(self, content: str) -> AsyncGenerator[str, None]:
        while content:
            yield content[0]
            content = content[1:]

    async def pipe(
        self,
        body: dict,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> AsyncGenerator[str, None]:
        self.emitter = __event_emitter__

        if not self.valves.DEEPSEEK_API_KEY or not self.valves.ANTHROPIC_API_KEY:
            yield json.dumps({"error": "Missing API key(s)"}, ensure_ascii=False)
            return

        # Prepare the payload for DeepClaude API
        payload = {
            "stream": self.valves.STREAM,
            "verbose": self.valves.VERBOSE,
            "messages": body.get("messages", []),
            "deepseek_config": {
                "body": {
                    "temperature": self.valves.TEMPERATURE,
                }
            },
            "anthropic_config": {
                "body": {
                    "temperature": self.valves.TEMPERATURE,
                }
            }
        }

        # Add system message if present in the body
        if "system" in body and body["system"]:
            payload["system"] = body["system"]

        # Transfer additional parameters from the request
        for key in ["max_tokens", "stop"]:
            if key in body:
                payload["anthropic_config"]["body"][key] = body[key]

        # Stream the response from DeepClaude API
        async for data in deepclaude_api_call(
            payload=payload,
            api_base_url=self.valves.DEEPCLAUDE_API_BASE_URL,
            deepseek_api_key=self.valves.DEEPSEEK_API_KEY,
            anthropic_api_key=self.valves.ANTHROPIC_API_KEY,
        ):
            if "error" in data:
                async for chunk in self._emit(data["error"]):
                    yield chunk
                return

            for choice in data.get("choices", []):
                delta = choice.get("delta", {})
                if content := delta.get("content", ""):
                    async for chunk in self._emit(content):
                        yield chunk
