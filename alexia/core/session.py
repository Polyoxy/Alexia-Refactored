# -*- coding: utf-8 -*-
"""
Manages the interactive chat session for Alexia.

This module contains the ChatSession class, which is responsible for the main
chat loop, handling user input, generating execution plans, and managing
multi-step tool execution with error handling and a current working directory.
"""

import asyncio
import json
import os
from typing import List, Dict, Optional, Any

from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status
from rich.rule import Rule
from rich.text import Text

from alexia.core.config import Config
from alexia.services.ollama_client import OllamaClient, OllamaError
from alexia.tools.registry import ToolRegistry
from alexia.tools.extended_tools import all_new_tools
from alexia.ui.display import (
    display_tool_request, 
    display_tool_result,
    display_process_table,
    display_plan,
    display_error,
    display_cwd_change
)

class ChatSession:
    """Represents and manages a single, tool-aware chat session."""

    def __init__(self, config: Config, client: OllamaClient, console: Console):
        self.config = config
        self.client = client
        self.console = console
        self.messages: List[Dict[str, str]] = []
        self.current_working_directory = os.getcwd()
        
        self.tool_registry = ToolRegistry(tools=all_new_tools)
        self.tool_prompt_string = self.tool_registry.generate_prompt_string().replace("You have access to the following tools.", "Available Tools:")
        
        self.system_prompt = self.config.system_prompt
        if self.tool_prompt_string:
            self.system_prompt = f"{self.config.system_prompt}\n\n{self.tool_prompt_string}"

    async def _get_user_input(self) -> str:
        """Gets input from the user, displaying the current working directory."""
        loop = asyncio.get_event_loop()
        prompt = Text.from_markup(f"[dim]({os.path.basename(self.current_working_directory)})[/dim] [bold green]>>> [/bold green]")
        return await loop.run_in_executor(None, lambda: self.console.input(prompt))

    async def _get_llm_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        full_response = ""
        with self.console.status("[bold yellow]Alexia is thinking...[/bold yellow]"):
            async for chunk in self.client.stream_chat(
                model=self.config.model,
                messages=messages,
                system_prompt=system_prompt
            ):
                token = chunk.get("message", {}).get("content", "")
                full_response += token
        return full_response

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        try:
            json_str = response
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            return None

    async def _confirm_action(self, prompt_text: str) -> bool:
        loop = asyncio.get_event_loop()
        while True:
            prompt = Text.from_markup(f"[bold yellow]{prompt_text} (y/n): [/bold yellow]")
            response = (await loop.run_in_executor(None, self.console.input, prompt)).lower().strip()
            if response == 'y': return True
            if response == 'n': return False
            self.console.print("[red]Invalid input. Please enter 'y' or 'n'.[/red]")

    async def _generate_plan(self, user_input: str) -> Optional[List[Dict]]:
        """Asks the AI to generate a plan of tool calls."""
        planning_prompt = (
            "You are a helpful AI assistant that creates a sequence of tool calls to fulfill a user's request. "
            f"The user's current working directory is '{self.current_working_directory}'. "
            "You must choose tools from the 'Available Tools' list. "
            "Respond ONLY with a single JSON object with a 'plan' key, which is an array of tool call objects. "
            "Each object in the array must be a valid tool call with 'tool_name' and 'arguments'.\n\n"
            f"{self.tool_prompt_string}"
        )
        
        plan_messages = [{"role": "user", "content": user_input}]
        response = await self._get_llm_response(plan_messages, planning_prompt)
        
        parsed_response = self._parse_json_response(response)
        if parsed_response and isinstance(parsed_response.get("plan"), list):
            # Validate that each step in the plan is a dictionary (a tool call)
            if all(isinstance(step, dict) for step in parsed_response["plan"]):
                return parsed_response["plan"]
        
        display_error(self.console, "Failed to generate a valid plan. The AI's response was not in the expected format. Please try rephrasing your request.")
        return None

    async def run(self):
        """Runs the main interactive chat loop with planning and execution phases."""
        self.console.print("[bold blue]Starting chat session. Type '/exit', '/quit', or press Ctrl+C to end.[/bold blue]")
        self.console.print(Rule(style="#666666"))
        self.console.print()

        try:
            while True:
                initial_user_input = await self._get_user_input()
                if initial_user_input.lower() in ["/exit", "/quit"]:
                    self.console.print("[bold blue]Ending session. Goodbye![/bold blue]")
                    break

                plan = await self._generate_plan(initial_user_input)
                if not plan:
                    continue

                plan_descriptions = [f"Use `{step.get('tool_name', 'unknown tool')}`" for step in plan]
                display_plan(self.console, plan_descriptions)

                if not await self._confirm_action("Proceed with this plan?"):
                    self.console.print("[bold red]Plan rejected by user.[/bold red]")
                    continue

                self.messages = [{"role": "user", "content": f"The user approved the plan for the request: '{initial_user_input}'. Execute it step-by-step."}]
                
                plan_failed = False
                last_tool_result = ""
                for i, step in enumerate(plan):
                    self.console.print(Rule(f"[bold cyan]Step {i+1}/{len(plan)}: {plan_descriptions[i]}[/bold cyan]", style="#666666"))
                    
                    tool_name = step.get('tool_name')
                    arguments = step.get('arguments', {})
                    tool = self.tool_registry.get_tool(tool_name)

                    if not tool:
                        display_error(self.console, f"Plan references an unknown tool: '{tool_name}'. Aborting.")
                        plan_failed = True
                        break

                    display_tool_request(self.console, tool_name, arguments)
                    
                    if not await self._confirm_action("Execute this step?"):
                        self.console.print("[bold red]Execution aborted by user.[/bold red]")
                        plan_failed = True
                        break
                    
                    if 'cwd' in tool.func.__code__.co_varnames:
                        arguments['cwd'] = self.current_working_directory

                    with self.console.status(f"[bold yellow]Executing tool: {tool_name}...[/bold yellow]"):
                        try:
                            loop = asyncio.get_event_loop()
                            tool_result = await loop.run_in_executor(None, lambda: tool.func(**arguments))
                            last_tool_result = str(tool_result)
                        except Exception as e:
                            tool_result = f"Error: An unexpected exception occurred: {e}"
                    
                    display_tool_result(self.console, str(tool_name), str(tool_result))
                    
                    if isinstance(tool_result, str) and tool_result.strip().startswith("Error:"):
                        self.console.print(f"[bold red]Step {i+1} failed. Aborting plan.[/bold red]")
                        plan_failed = True
                        break
                    
                    if tool.name == 'change_directory':
                        self.current_working_directory = tool_result
                        display_cwd_change(self.console, self.current_working_directory)

                    self.messages.append({"role": "user", "content": f"Step {i+1} ('{plan_descriptions[i]}') was completed successfully. The tool '{tool_name}' returned: {tool_result}"})

                if not plan_failed:
                    self.console.print(Rule("[bold green]Plan Finished[/bold green]", style="#666666"))
                    final_prompt = (
                        "The execution plan is complete. Based on the history and the final tool result below, "
                        "provide a concise, natural-language summary to the user about what was accomplished.\n\n"
                        f"Final Information:\n---\n{last_tool_result}\n---"
                    )
                    self.messages.append({"role": "user", "content": final_prompt})
                    final_response = await self._get_llm_response(self.messages, self.system_prompt)
                    self.console.print(Markdown(final_response, code_theme="monokai"))
                
                self.console.print()
                self.console.print(Rule(style="#666666"))
                self.console.print()

        except (KeyboardInterrupt, asyncio.CancelledError):
            self.console.print("\n[bold blue]Session ended. Goodbye![/bold blue]")

