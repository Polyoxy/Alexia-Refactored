# -*- coding: utf-8 -*-
"""
This module handles all user interface rendering for the Alexia application.

It uses the 'rich' library to create beautifully formatted output in the terminal,
including the welcome banner, markdown rendering, tables, and panels.
"""

import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Any

import psutil
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

# --- Private Helper Functions ---

def _get_ascii_art() -> str:
    """Returns the scaled-down ASCII art banner."""
    return r"""                     
                               ..       
                       .,;. .;:.        
            ,:.     .'lOXx,:xl.         
            lKd. .ck0KKOXK0O:           
           .dNNOkKNNXO;;0Nx'            
           .kWWWWWXo;. 'ko.             
         'lONWWWWNx.   ..               
       'oKNWWWWWWWXl'.                  
       ..':kNWX0KNWNKd.                 
           lXO;..';cll,                 
          .lo.                          
           .                            
"""

def _get_gpu_info() -> str:
    """Attempts to get GPU information from common CLI tools."""
    command = "where" if platform.system() == "Windows" else "which"
    try:
        # Check for NVIDIA GPU
        if subprocess.run([command, 'nvidia-smi'], capture_output=True, text=True, check=False).returncode == 0:
            result = subprocess.check_output(['nvidia-smi', '--query-gpu=gpu_name', '--format=csv,noheader,nounits'], text=True)
            return result.strip().split('\n')[0]
        # Check for AMD GPU (simple detection)
        if subprocess.run([command, 'radeontop'], capture_output=True, text=True, check=False).returncode == 0:
            return "AMD GPU (detected)"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "N/A"

def _get_system_info(model_name: str) -> Dict[str, str]:
    """Gathers and formats key system hardware and software information."""
    try:
        mem = psutil.virtual_memory()
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        days, rem = divmod(uptime.total_seconds(), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m"

        return {
            "OS": f"{platform.system()} {platform.release()}",
            "Uptime": uptime_str,
            "CPU": f"{platform.processor() or platform.machine()} ({psutil.cpu_count(logical=False)}c/{psutil.cpu_count(logical=True)}t)",
            "GPU": _get_gpu_info(),
            "Memory": f"{mem.used / 1024**3:.1f}GB / {mem.total / 1024**3:.1f}GB",
            "Model": model_name
        }
    except Exception:
        return {k: "Unknown" for k in ["OS", "Uptime", "CPU", "GPU", "Memory", "Model"]}

# --- Public Display Functions ---

def display_welcome_banner(console: Console, model_name: str):
    """Displays the startup banner with ASCII art and system info, aligned manually."""
    art_lines = _get_ascii_art().split('\n')
    max_art_width = max(len(line) for line in art_lines) if art_lines else 0

    info_data = _get_system_info(model_name)
    user = os.environ.get('USER', 'dev') or os.environ.get('USERNAME', 'dev')
    hostname = platform.node()
    header = f"[bold white]{user}@{hostname}[/bold white]"
    info_lines = [header] + [f"[bold white]{k}:[/bold white] [white]{v}[/white]" for k, v in info_data.items()]

    max_lines = max(len(art_lines), len(info_lines))
    
    console.print() # Top margin
    for i in range(max_lines):
        art_line = art_lines[i] if i < len(art_lines) else ''
        info_line = info_lines[i] if i < len(info_lines) else ''
        
        # Create a padded art line to ensure alignment
        padded_art = f"{art_line:<{max_art_width}}"
        
        console.print(f"[cyan]{padded_art}[/cyan]  {info_line}")
    console.print() # Bottom margin

def display_markdown(console: Console, text: str):
    """Renders and prints a string as markdown."""
    markdown = Markdown(text, code_theme="dark+", style="default")
    console.print(markdown)

def display_models_table(console: Console, models: List[Dict[str, Any]]):
    """Displays a list of models in a formatted table."""
    table = Table(title="Available Ollama Models", border_style="green")
    table.add_column("Model Name", style="cyan", no_wrap=True)
    table.add_column("Size", style="magenta")
    table.add_column("Modified", style="yellow")

    for model in models:
        size_gb = model.get('size', 0) / 1024**3
        modified_at = model.get('modified_at', '').split('T')[0]
        table.add_row(model.get('name'), f"{size_gb:.2f} GB", modified_at)
    
    console.print(table)

def display_error(console: Console, message: str):
    """Displays a formatted error message."""
    console.print(Panel(Text(message, justify="center"), title="[bold red]Error[/bold red]", border_style="red"))

def display_tool_request(console: Console, tool_name: str, arguments: Dict[str, Any]):
    """Displays a formatted panel for a tool request."""
    # Format arguments for display
    args_text = "\n".join(f"  - {k}: [bold]{v}[/bold]" for k, v in arguments.items())
    
    # Create a more noticeable panel
    panel = Panel(
        f"[bold]Tool:[/bold] [cyan]{tool_name}[/cyan]\n\n[bold]Arguments:[/bold]\n{args_text}",
        title="[bold yellow]🛠️  Tool Execution Request[/bold yellow]",
        title_align="left",
        border_style="yellow",
        style="dim",
        padding=(1, 2),
        expand=False
    )
    
    # Print some spacing before and after the panel
    console.print()
    console.print(panel)
    console.print()

def display_tool_result(console: Console, tool_name: str, result: str):
    """Displays the result of a tool execution in a formatted panel."""
    console.print(
        Panel(
            Text(result, overflow="ellipsis"),
            title=f"[bold green]Result from {tool_name}[/bold green]",
            border_style="green",
            expand=False
        )
    )

def prompt_for_confirmation(console: Console, prompt_text: str = "Proceed?") -> bool:
    """Prompts the user for a 'y/n' confirmation and returns a boolean."""
    # Create a more noticeable prompt
    console.print("\n[bold yellow]⚠️  Confirmation Required[/bold yellow]")
    console.print(f"[bold]{prompt_text}[/bold]")
    
    # Keep asking until we get a valid response
    while True:
        response = console.input("[bold cyan]›[/bold cyan] [bold]Confirm?[/bold] (y/n): ").lower().strip()
        if response in ('y', 'yes'):
            console.print("[green]✓ Confirmed[/green]\n")
            return True
        elif response in ('n', 'no'):
            console.print("[red]✗ Cancelled[/red]\n")
            return False
        else:
            console.print("[yellow]Please enter 'y' for yes or 'n' for no[/yellow]")

def display_info(console: Console, message: str):
    """Displays a formatted informational message."""
    console.print(f"[bold green]Info:[/bold green] {message}")
