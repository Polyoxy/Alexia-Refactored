# -*- coding: utf-8 -*-
"""
Manages the interactive chat session for Alexia.

This module contains the ChatSession class, which is responsible for the main
chat loop, handling user input, managing conversation history, and interacting
with the Ollama API to stream responses.
"""

import asyncio
import json
import os
from typing import List, Dict, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status
from rich.rule import Rule
from rich.style import Style

from alexia.core.config import Config
from alexia.services.ollama_client import OllamaClient
from alexia.tools.registry import ToolRegistry
from alexia.tools.file_system import read_file_tool, list_directory_tool, write_file_tool
from alexia.ui.display import display_tool_request, display_tool_result, prompt_for_confirmation

class ChatSession:
    """Represents and manages a single, tool-aware chat session with persistent memory."""

    def __init__(self, config: Config, client: OllamaClient, console: Console):
        import os
        import platform
        import json
        
        self.config = config
        self.client = client
        self.console = console
        self.messages: List[Dict[str, str]] = []
        
        # Initialize session state
        self.os_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'node': platform.node(),
            'python_version': platform.python_version()
        }
        
        # Set initial directory to user's home
        self.current_dir = os.path.expanduser("~")
        os.chdir(self.current_dir)
        
        # Initialize session memory
        self.session_memory = {
            'os_info': self.os_info,
            'current_dir': self.current_dir,
            'command_history': [],
            'context': {}
        }
        
        # Setup the tool registry
        self.tool_registry = ToolRegistry(tools=[read_file_tool, list_directory_tool, write_file_tool])
        self.tool_prompt = self.tool_registry.generate_prompt_string()
        
        # Update system prompt with session context
        self._update_system_prompt()
        
    def _update_system_prompt(self):
        """Update the system prompt with current session context."""
        context = (
            f"System Information:\n"
            f"- OS: {self.os_info['system']} {self.os_info['release']}\n"
            f"- Current Directory: {self.current_dir}\n"
            f"- Python: {self.os_info['python_version']}\n"
            "\nYou have access to the following tools:"
        )
        
        self.system_prompt = (
            f"{self.config.system_prompt}\n\n"
            f"{context}\n\n"
            f"{self.tool_prompt}\n\n"
            "Remember the current directory and OS context when performing operations. "
            "Always use absolute paths or paths relative to the current directory.\n"
            "The current working directory has been set to the user's home directory."
        )

    def _get_separator(self, width: int = 60) -> str:
        """Get a consistent separator line."""
        return "─" * min(width, 80)  # Cap at 80 characters width

    async def _get_user_input(self, prompt: str = "❯") -> str:
        """Gets input from the user asynchronously with a styled prompt."""
        from rich.text import Text
        
        # Format the directory path to be more compact
        display_path = self.current_dir
        try:
            # Make path relative to home directory if possible
            home = os.path.expanduser("~")
            if display_path.startswith(home):
                display_path = f"~{os.sep}{display_path[len(home):]}"
        except Exception:
            pass
            
        # Get username
        import getpass
        username = getpass.getuser()
        
        # Create a styled prompt
        prompt_text = Text()
        prompt_text.append(f"{username} ", style="bold cyan")
        prompt_text.append("in ", style="dim")
        prompt_text.append(f"{display_path}", style="bold blue")
        prompt_text.append("\n")
        prompt_text.append(f"{prompt} ", style="bold green")
        
        # Get user input asynchronously
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(
            None, 
            lambda: self.console.input(prompt_text)
        )
        
        # Add to command history
        if user_input.strip() and not user_input.startswith('!'):
            self.session_memory['command_history'].append({
                'command': user_input,
                'timestamp': self._get_timestamp(),
                'type': 'ai_command'
            })
            
        return user_input

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
        # Add a single newline after AI response for better readability
        if full_response and not full_response.endswith("\n"):
            full_response += "\n"
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

    def _update_current_dir(self, new_dir: str) -> bool:
        """Update the current working directory and session state."""
        import os
        try:
            # Handle home directory shortcut
            if new_dir == '~' or not new_dir:
                new_dir = os.path.expanduser("~")
            
            # Convert relative paths to absolute
            if not os.path.isabs(new_dir):
                new_dir = os.path.abspath(os.path.join(self.current_dir, new_dir))
            
            # Verify the directory exists
            if not os.path.isdir(new_dir):
                return False
                
            # Update the current directory
            os.chdir(new_dir)
            self.current_dir = os.getcwd()
            self.session_memory['current_dir'] = self.current_dir
            
            # Update the system prompt with new directory
            self._update_system_prompt()
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error changing directory: {e}[/red]")
            return False

    async def _execute_shell_command(self, command: str) -> str:
        """Executes a shell command and returns its output."""
        import os
        import subprocess
        
        try:
            # Remove any leading '!' if present and strip whitespace
            command = command.lstrip('!').strip()
            if not command:
                return "No command provided"
                
            # Handle cd command specially to maintain session state
            if command.startswith('cd '):
                new_dir = command[3:].strip()
                if self._update_current_dir(new_dir):
                    return f"Changed directory to: {self.current_dir}"
                return f"[red]Directory not found: {new_dir}[/red]"
                
            # Execute other commands
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Update command history
            self.session_memory['command_history'].append({
                'command': command,
                'timestamp': self._get_timestamp(),
                'success': result.returncode == 0
            })
            
            # Format the output
            output = []
            if result.stdout:
                output.append(result.stdout.strip())
            if result.stderr:
                output.append(f"[red]Error (code {result.returncode}):[/red]\n{result.stderr.strip()}")
                
            return "\n".join(output) if output else "Command executed (no output)"
            
        except Exception as e:
            return f"[red]Error executing command: {str(e)}[/red]"
            
    def _get_timestamp(self) -> str:
        """Get current timestamp in a readable format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def run(self):
        """Runs the main interactive chat loop with tool handling and graceful exit."""
        welcome_msg = (
            "[bold blue]Alexia is ready![/bold blue]\n"
            "[dim]Type your message or use '!' for shell commands (e.g., '!dir')[/dim]"
        )
        
        # Print welcome message
        self.console.print(welcome_msg)
        self.console.print()  # Single newline after welcome

        try:
            while True:
                user_input = await self._get_user_input()
                
                # Handle empty input
                if not user_input.strip():
                    continue
                    
                # Handle exit commands
                if user_input.lower() in ["/exit", "/quit"]:
                    self.console.print("[bold blue]Ending session. Goodbye![/bold blue]")
                    break
                    
                # Handle shell commands (prefixed with !)
                if user_input.startswith('!'):
                    command = user_input[1:].strip()
                    if not command:
                        continue
                        
                    # Special handling for cd command to maintain directory state
                    if command.startswith('cd '):
                        try:
                            new_dir = command[3:].strip()
                            if not new_dir:
                                # If just 'cd', go to home directory
                                new_dir = os.path.expanduser("~")
                            os.chdir(new_dir)
                            self.console.print(f"[green]Changed directory to: {os.getcwd()}[/green]")
                        except Exception as e:
                            self.console.print(f"[red]Error changing directory: {e}[/red]")
                        continue
                        
                    # Execute other commands in shell
                    self.console.print(f"[dim]Executing: {command}[/dim]")
                    output = await self._execute_shell_command(command)
                    self.console.print(output)
                    self.console.print()  # Add extra line for spacing
                    continue

                self.messages.append({"role": "user", "content": user_input})
                llm_response = await self._get_llm_response()

                # Check if the response is a JSON tool request
                tool_request = None
                response_text = llm_response.strip()
                
                # Try direct JSON parse first
                if response_text.startswith('{') and 'tool_name' in response_text:
                    try:
                        tool_request = json.loads(response_text)
                    except json.JSONDecodeError:
                        pass
                
                # If that fails, try extracting from markdown code block
                if not tool_request:
                    tool_request = self._parse_tool_request(response_text)
                else:
                    tool_request = None

                if tool_request:
                    tool_name = tool_request.get('tool_name')
                    arguments = tool_request.get('arguments', {})
                    tool = self.tool_registry.get_tool(tool_name)

                    if not tool:
                        self.console.print(f"[bold red]Error: AI requested an unknown tool: '{tool_name}'[/bold red]")
                        continue

                    # Show the tool request and get confirmation
                    display_tool_request(self.console, tool_name, arguments)
                    
                    # Get user confirmation
                    try:
                        loop = asyncio.get_event_loop()
                        confirmed = await loop.run_in_executor(
                            None, 
                            lambda: prompt_for_confirmation(self.console, f"Execute {tool_name}?")
                        )

                        if not confirmed:
                            self.console.print("[bold red]Operation cancelled by user.[/bold red]")
                            self.messages.pop()
                            continue
                            
                    except Exception as e:
                        self.console.print(f"[bold red]Error getting confirmation: {e}[/bold red]")
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
