# -*- coding: utf-8 -*-
"""
Provides an extended set of agentic tools for the Alexia AI assistant.

This module includes tools for advanced file system operations, code analysis,
web browsing, command execution, and more. Each tool is designed to be
registered with the ToolRegistry.
"""

import os
import platform
import subprocess
import webbrowser
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, unquote

import psutil
import requests
from alexia.tools.tool import Tool
from alexia.core.process_manager import ProcessManager

# --- Placeholder Functions ---
def _unimplemented_func(*args, **kwargs) -> str:
    """A placeholder for functions that are not yet implemented."""
    return "Error: This tool's function has not been implemented yet."

# --- CWD and Process Tools ---
def _change_directory_func(path: str, cwd: str) -> str:
    """Changes the current working directory."""
    try:
        # Handle tilde expansion for home directory
        expanded_path = os.path.expanduser(path)
        # Join with CWD to handle relative paths
        new_path = os.path.join(cwd, expanded_path)
        
        if os.path.isdir(new_path):
            return os.path.abspath(new_path)
        return f"Error: Directory '{new_path}' not found."
    except Exception as e:
        return f"Error changing directory: {e}"


def _list_processes_func() -> List[Dict[str, Any]]:
    """Gathers a list of all running processes and their key metrics."""
    processes = []
    managed_pids = ProcessManager().list_pids()
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            p_info = proc.info
            p_info['managed'] = 'Yes' if p_info['pid'] in managed_pids else 'No'
            processes.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)

def _start_process_func(command: str, cwd: str) -> str:
    """
    Starts a long-running command (like a web server) in the background.
    It waits 2 seconds and returns its initial output and PID.
    """
    manager = ProcessManager()
    pid = manager.start_process(command, cwd)
    if not pid:
        return "Error: Failed to start the process."

    initial_output = manager.get_output(pid, wait_for_output_seconds=2.0)
    output_str = "".join(initial_output) if initial_output else "No initial output captured."

    return (
        f"Successfully started process with PID: {pid}.\n"
        f"Initial output:\n---\n{output_str}\n---\n"
        "Use 'stop_process' to terminate it."
    )

def _run_shell_command_func(command: str, cwd: str) -> str:
    """
    Executes a shell command that is expected to finish and returns its output.
    """
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, 
            text=True, timeout=300, cwd=cwd
        )
        output = f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: Command failed with exit code {e.returncode}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def _stop_process_func(pid: int) -> str:
    """Stops a background process managed by Alexia."""
    if ProcessManager().stop_process(pid):
        return f"Successfully stopped process with PID {pid}."
    return f"Error: Process with PID {pid} is not managed by Alexia or was already stopped."


# --- Web, Browser, and Resource Tools ---
def _read_url_content_func(url: str) -> str:
    """
    Reads the raw text content from a URL. 
    It automatically converts standard GitHub file URLs to their raw format.
    """
    try:
        # If it's a GitHub file URL, convert it to the raw content URL
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to fetch content from URL. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def _open_browser_url_func(url: str) -> str:
    try:
        webbrowser.open(url)
        return f"Successfully opened {url} in the browser."
    except Exception as e:
        return f"Error opening URL: {e}"

# --- File System Tools ---
def _view_file_func(file_path: str, cwd: str) -> str:
    """
    Reads the content of a file. It can handle both regular file paths
    and file:// URIs.
    """
    try:
        if file_path.startswith('file:///'):
            parsed_uri = urlparse(file_path)
            if platform.system() == "Windows":
                file_path = parsed_uri.path[1:]
            else:
                file_path = parsed_uri.path
            file_path = unquote(file_path)
        
        full_path = os.path.join(cwd, file_path)
        
        if not os.path.isfile(full_path):
            return f"Error: File not found at '{full_path}'."
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error: Could not read file: {e}"

# --- Tool Definitions ---
all_new_tools: List[Tool] = [
    Tool(
        name="change_directory",
        description="Changes the current working directory for subsequent tool calls.",
        func=_change_directory_func,
        args_schema=[{"name": "path", "type": "string", "description": "The target directory path."}]
    ),
    Tool(
        name="run_shell_command",
        description="Runs a shell command that finishes on its own (like git clone, ls, cat) and returns its output.",
        func=_run_shell_command_func,
        args_schema=[{"name": "command", "type": "string", "description": "The command to execute."}]
    ),
    Tool(
        name="view_file",
        description="Views the entire contents of a specified local file. Can handle both normal paths and file:// URIs.",
        func=_view_file_func,
        args_schema=[{"name": "file_path", "type": "string", "description": "The local path or file URI to the file to view."}]
    ),
    Tool(
        name="read_url_content",
        description="Reads the raw text content from a URL. Best for links to raw files like READMEs on GitHub.",
        func=_read_url_content_func,
        args_schema=[{"name": "url", "type": "string", "description": "The URL to read content from."}]
    ),
    Tool(
        name="start_process",
        description="Starts a long-running process (like a web server) in the background and returns its initial output and PID.",
        func=_start_process_func,
        args_schema=[{"name": "command", "type": "string", "description": "The command to execute."}]
    ),
    Tool(
        name="stop_process",
        description="Stops a background process that was started by Alexia.",
        func=_stop_process_func,
        args_schema=[{"name": "pid", "type": "integer", "description": "The PID of the process to stop."}]
    ),
    Tool(
        name="list_processes",
        description="Lists all running processes, indicating which are managed by Alexia.",
        func=_list_processes_func,
        args_schema=[]
    ),
    Tool(
        name="open_browser_url",
        description="Opens a specified URL in the user's default web browser.",
        func=_open_browser_url_func,
        args_schema=[{"name": "url", "type": "string", "description": "The URL to open."}]
    ),
]
