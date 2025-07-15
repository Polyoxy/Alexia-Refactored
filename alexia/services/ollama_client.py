# -*- coding: utf-8 -*-
"""
This module provides a client for interacting with the Ollama API.

It handles sending requests, managing streaming responses, and fetching
model information, encapsulating all direct communication with the Ollama service.
"""

import json
import httpx
from typing import Dict, List, Any, AsyncIterator, Optional

class OllamaError(Exception):
    """Custom exception for Ollama API errors."""
    pass

class OllamaClient:
    """An asynchronous client for the Ollama API that supports the async context manager protocol."""

    def __init__(self, host: str, timeout: int = 120):
        self.host = host.rstrip('/')
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager and close the client."""
        await self._client.aclose()

    async def health_check(self) -> bool:
        """Performs a simple health check to see if the Ollama server is running."""
        try:
            response = await self._client.get(self.host, timeout=5)
            return response.status_code == 200 and "Ollama is running" in response.text
        except httpx.RequestError:
            return False

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Fetches the list of available models from the Ollama host."""
        try:
            response = await self._client.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except httpx.Timeout as e:
            raise OllamaError(f"Connection to {self.host} timed out. Please ensure Ollama is running and accessible.") from e
        except httpx.RequestError as e:
            raise OllamaError(f"Could not fetch models from Ollama. Is it running? Details: {e}") from e

    async def stream_chat(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Streams a chat response from the Ollama API.
        """
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages

        payload = {
            "model": model,
            "messages": full_messages,
            "stream": True
        }

        try:
            async with self._client.stream("POST", f"{self.host}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        if chunk.get("error"):
                            raise OllamaError(chunk["error"])
                        yield chunk
        except httpx.RequestError as e:
            raise OllamaError(f"Network error during chat stream: {e}") from e
