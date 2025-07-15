# -*- coding: utf-8 -*-
"""
Manages the interactive chat session for Alexia.

This module contains the ChatSession class, which is responsible for the main
chat loop, handling user input, managing conversation history, and interacting
with the Ollama API to stream responses. It supports multi-step tool execution.
"""

import asyncio
import json
from typing import List, Dict, Optional, Any

from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status
from rich.rule import Rule
from rich.text import Text

from alexia.core.config import Config
from alexia.services.ollama_client import OllamaClient
from alexia.tools.registry import ToolRegistry
from alexia.tools.extended_tools import all_new_tools
from alexia.ui.display import (
    display_tool_request, 
    display_tool_result,
    display_process_table
)

class ChatSession:
    """Represents and manages a single, tool-aware chat session."""

    def __init__(self, config: Config, client: OllamaClient, console: Console):
        self.config = config
        self.client = client
        self.console = console
        self.messages: List[Dict[str, str]] = []
        
        # This will now register the updated tool list from extended_tools.py
        self.tool_registry = ToolRegistry(tools=all_new_tools)
        self.tool_prompt = self.tool_registry.generate_prompt_string()
        
        self.system_prompt = self.config.system_prompt
        if self.tool_prompt:
            self.system_prompt = f"{self.config.system_prompt}\n\n{self.tool_prompt}"

    async def _get_user_input(self, prompt: str = "[bold green]>>> [/bold green]") -> str:
        """Gets input from the user asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.console.input(prompt))

    async def _get_llm_response(self) -> str:
        """Gets a complete response from the LLM."""
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
        """
        Parses a tool request JSON from the LLM's response.
        This is made more robust to handle responses with or without markdown code blocks.
        """
        try:
            json_str = response
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            
            data = json.loads(json_str.strip())

            if isinstance(data, dict) and 'tool_name' in data and 'arguments' in data:
                return data
        except (json.JSONDecodeError, IndexError):
            return None
        return None

    async def run(self):
        """Runs the main interactive chat loop with multi-step tool handling."""
        self.console.print("[bold blue]Starting chat session. Type '/exit', '/quit', or press Ctrl+C to end.[/bold blue]")
        self.console.print(Rule(style="#666666"))
        self.console.print()

        try:
            while True:
                initial_user_input = await self._get_user_input()
                if initial_user_input.lower() in ["/exit", "/quit"]:
                    self.console.print("[bold blue]Ending session. Goodbye![/bold blue]")
                    break

                self.messages.append({"role": "user", "content": initial_user_input})
                
                history_len_before_tools = len(self.messages)
                
                while True: 
                    llm_response = await self._get_llm_response()
                    tool_request = self._parse_tool_request(llm_response)

                    if not tool_request:
                        self.console.print(Markdown(llm_response, code_theme="monokai"))
                        self.messages.append({"role": "assistant", "content": llm_response})
                        break 

                    tool_name = tool_request.get('tool_name')
                    arguments = tool_request.get('arguments', {})
                    tool = self.tool_registry.get_tool(tool_name)

                    if not tool:
                        self.console.print(f"[bold red]Error: AI requested an unknown tool: '{tool_name}'[/bold red]")
                        break 

                    display_tool_request(self.console, tool_name, arguments)
                    
                    confirmed = False
                    loop = asyncio.get_event_loop()
                    while True:
                        prompt = Text.from_markup("[bold yellow]Proceed? (y/n): [/bold yellow]")
                        response = (await loop.run_in_executor(None, self.console.input, prompt)).lower().strip()
                        if response == 'y':
                            confirmed = True
                            break
                        if response == 'n':
                            confirmed = False
                            break
                        self.console.print("[red]Invalid input. Please enter 'y' or 'n'.[/red]")

                    if not confirmed:
                        self.console.print("[bold red]Operation cancelled by user.[/bold red]")
                        self.messages = self.messages[:history_len_before_tools]
                        break 

                    tool_message_content = ""
                    with self.console.status(f"[bold yellow]Executing tool: {tool_name}...[/bold yellow]"):
                        try:
                            tool_result = await loop.run_in_executor(None, lambda: tool.func(**arguments))
                        except Exception as e:
                            self.console.print(f"[bold red]Error executing tool '{tool_name}': {e}[/bold red]")
                            break

                    if tool.name == 'list_processes' and isinstance(tool_result, list):
                        display_process_table(self.console, tool_result)
                        top_5 = tool_result[:5]
                        summary = ", ".join([p.get('name', 'N/A') for p in top_5])
                        tool_message_content = f"Tool '{tool_name}' executed. Displayed a list of {len(tool_result)} processes. The top processes are: {summary}."
                    else:
                        display_tool_result(self.console, str(tool_name), str(tool_result))
                        tool_message_content = f"Tool '{tool_name}' was executed and returned: {tool_result}"

                    # --- Final, context-aware follow-up prompt ---
                    follow_up_prompt = (
                        f"The user's original request was: '{initial_user_input}'.\n"
                        f"You just executed the tool '{tool_name}' which returned: '{tool_message_content}'.\n"
                        "Based on the original request and the output you received, determine the next logical step. "
                        "If more steps are required, call the next tool using the required JSON format. "
                        "If the user's request is fully complete, provide a final, natural-language answer."
                    )
                    self.messages.append({
                        "role": "user", 
                        "content": follow_up_prompt
                    })

                self.console.print()
                self.console.print(Rule(style="#666666"))
                self.console.print()

        except (KeyboardInterrupt, asyncio.CancelledError):
            self.console.print("\n[bold blue]Session ended. Goodbye![/bold blue]")
