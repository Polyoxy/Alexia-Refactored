# -*- coding: utf-8 -*-
"""
Manages the interactive chat session for Alexia.

This module contains the ChatSession class, which is responsible for the main
chat loop, handling user input, managing conversation history, and interacting
with the Ollama API to stream responses.
"""

import asyncio
import json
from typing import List, Dict, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status
from rich.rule import Rule
from rich.style import Style

from alexia.core.config import Config
from alexia.services.ollama_client import OllamaClient
from alexia.tools.registry import ToolRegistry
from alexia.tools.file_system import read_file_tool, list_directory_tool
from alexia.ui.display import display_tool_request, display_tool_result, prompt_for_confirmation

class ChatSession:
    """Represents and manages a single, tool-aware chat session."""

    def __init__(self, config: Config, client: OllamaClient, console: Console):
        self.config = config
        self.client = client
        self.console = console
        self.messages: List[Dict[str, str]] = []
        
        # Setup the tool registry
        self.tool_registry = ToolRegistry(tools=[read_file_tool, list_directory_tool])
        self.tool_prompt = self.tool_registry.generate_prompt_string()
        
        # Combine system prompt with tool prompt
        self.system_prompt = self.config.system_prompt
        if self.tool_prompt:
            self.system_prompt = f"{self.config.system_prompt}\n\n{self.tool_prompt}"

    async def _get_user_input(self, prompt: str = "[bold green]>>> [/bold green]") -> str:
        """Gets input from the user asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.console.input(prompt))

    async def _get_llm_response(self) -> str:
        """Gets a complete response from the LLM, streaming enabled."""
        full_response = ""
        with self.console.status("[bold yellow]Alexia is thinking...[/bold yellow]"):
            async for chunk in self.client.stream_chat(
                model=self.config.model,
                messages=self.messages,
                system_prompt=self.system_prompt
            ):
                token = chunk.get("message", {}).get("content", "")
                full_response += token
        return full_response

    def _parse_tool_request(self, response: str) -> Optional[Dict]:
        """Parses a tool request JSON from the LLM's response."""
        try:
            # The response might be embedded in markdown, so we extract it
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            
            data = json.loads(response.strip())
            if isinstance(data, dict) and 'tool_name' in data and 'arguments' in data:
                return data
        except (json.JSONDecodeError, IndexError):
            return None
        return None

    async def run(self):
        """Runs the main interactive chat loop with tool handling and graceful exit."""
        self.console.print("[bold blue]Starting chat session. Type '/exit', '/quit', or press Ctrl+C to end.[/bold blue]")
        self.console.print(Rule(style="#666666"))  # Subtle gray separator
        self.console.print()  # Add extra line for spacing

        try:
            while True:
                user_input = await self._get_user_input()
                if user_input.lower() in ["/exit", "/quit"]:
                    self.console.print("[bold blue]Ending session. Goodbye![/bold blue]")
                    break

                self.messages.append({"role": "user", "content": user_input})
                llm_response = await self._get_llm_response()

                tool_request = self._parse_tool_request(llm_response)
                if tool_request:
                    tool_name = tool_request.get('tool_name')
                    arguments = tool_request.get('arguments', {})
                    tool = self.tool_registry.get_tool(tool_name)

                    if not tool:
                        self.console.print(f"[bold red]Error: AI requested an unknown tool: '{tool_name}'[/bold red]")
                        continue

                    display_tool_request(self.console, tool_name, arguments)
                    
                    loop = asyncio.get_event_loop()
                    confirmed = await loop.run_in_executor(None, lambda: prompt_for_confirmation(self.console))

                    if not confirmed:
                        self.console.print("[bold red]Operation cancelled by user.[/bold red]")
                        self.messages.pop()
                        continue
                    
                    with self.console.status(f"[bold yellow]Executing tool: {tool_name}...[/bold yellow]"):
                        try:
                            tool_result = await loop.run_in_executor(None, lambda: tool.func(**arguments))
                        except Exception as e:
                            self.console.print(f"[bold red]Error executing tool '{tool_name}': {e}[/bold red]")
                            continue

                    display_tool_result(self.console, tool_name, tool_result)

                    tool_message = f"Tool '{tool_name}' was executed and returned:\n---\n{tool_result}\n---\nBased on this, please provide the final answer to the user."
                    self.messages.append({"role": "user", "content": tool_message})

                    final_response = await self._get_llm_response()
                    self.console.print(Markdown(final_response))
                    self.messages.append({"role": "assistant", "content": final_response})
                else:
                    self.console.print(Markdown(llm_response))
                    self.messages.append({"role": "assistant", "content": llm_response})
                
                self.console.print()  # Add extra line for spacing
                self.console.print(Rule(style="#666666"))  # Subtle gray separator
                self.console.print()  # Add extra line for spacing

        except (KeyboardInterrupt, asyncio.CancelledError):
            self.console.print("\n[bold blue]Session ended. Goodbye![/bold blue]")
