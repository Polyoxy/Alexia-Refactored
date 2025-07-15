# -*- coding: utf-8 -*-
"""
Provides an extended set of agentic tools for the Alexia AI assistant.

This module includes tools for advanced file system operations, code analysis,
web browsing, command execution, and more. Each tool is designed to be
registered with the ToolRegistry.
"""

import os
import subprocess
import webbrowser
from typing import List

from alexia.tools.tool import Tool

# --- Placeholder Functions ---
# These are placeholder implementations. You would replace these with your
# actual business logic (e.g., using libraries like 'requests', 'beautifulsoup4',
# 'ast', etc.)

def _unimplemented_func(*args, **kwargs) -> str:
    """A placeholder for functions that are not yet implemented."""
    return "Error: This tool's function has not been implemented yet."

# --- File System Tools ---

def _create_file_func(file_path: str, content: str = "") -> str:
    """Creates a new file and optionally writes content to it."""
    try:
        expanded_path = os.path.expanduser(file_path)
        if os.path.exists(expanded_path):
            return f"Error: File already exists at '{expanded_path}'. Use 'replace_file_content' to modify it."
        
        dir_path = os.path.dirname(expanded_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            
        with open(expanded_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created file at '{expanded_path}'."
    except Exception as e:
        return f"Error: Failed to create file: {e}"

def _replace_file_content_func(file_path: str, new_content: str) -> str:
    """Replaces the entire content of an existing file."""
    try:
        expanded_path = os.path.expanduser(file_path)
        if not os.path.isfile(expanded_path):
            return f"Error: File not found at '{expanded_path}'."
        with open(expanded_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"Successfully replaced content of file '{expanded_path}'."
    except Exception as e:
        return f"Error: Failed to replace file content: {e}"

def _view_file_func(file_path: str) -> str:
    """Reads and returns the content of a file."""
    try:
        expanded_path = os.path.expanduser(file_path)
        if not os.path.isfile(expanded_path):
            return f"Error: File not found at '{expanded_path}'."
        with open(expanded_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: Could not read file: {e}"

def _find_by_name_func(name: str, search_dir: str = ".") -> str:
    """Searches for files and directories by name."""
    try:
        search_dir = os.path.expanduser(search_dir)
        results = []
        for root, dirs, files in os.walk(search_dir):
            if name in dirs or name in files:
                results.append(os.path.join(root, name))
        if not results:
            return f"No files or directories found with the name '{name}' in '{search_dir}'."
        return "\n".join(results)
    except Exception as e:
        return f"Error during search: {e}"

def _grep_search_func(pattern: str, search_dir: str = ".") -> str:
    """Searches for a pattern within files in a directory."""
    # This is a simplified implementation. A real implementation would be more robust.
    try:
        search_dir = os.path.expanduser(search_dir)
        results = []
        for root, _, files in os.walk(search_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f):
                            if pattern in line:
                                results.append(f"{file_path}:{i+1}:{line.strip()}")
                except (IOError, OSError):
                    continue # Skip files that can't be opened
        if not results:
            return f"No matches found for pattern '{pattern}' in '{search_dir}'."
        return "\n".join(results)
    except Exception as e:
        return f"Error during grep search: {e}"

def _list_dir_func(directory_path: str = ".") -> str:
    """Lists the contents of a specified directory."""
    try:
        expanded_path = os.path.expanduser(directory_path)
        if not os.path.isdir(expanded_path):
            return f"Error: Directory not found at '{expanded_path}'."
        items = os.listdir(expanded_path)
        return "\n".join(items)
    except Exception as e:
        return f"Error: Failed to list directory contents: {e}"


# --- Code Analysis Tools ---

def _view_code_item_func(file_path: str, item_name: str) -> str:
    """Views a specific code item (e.g., function or class) in a file."""
    # A real implementation would use Abstract Syntax Trees (AST) for accuracy.
    return _unimplemented_func(file_path, item_name)

def _codebase_search_func(query: str) -> str:
    """Finds relevant code snippets across the codebase based on a natural language query."""
    # A real implementation would likely use embedding-based semantic search.
    return _unimplemented_func(query)


# --- Command Execution Tools ---

def _run_command_func(command: str) -> str:
    """Executes a terminal command. Use with extreme caution."""
    # SECURITY WARNING: Executing arbitrary commands is dangerous.
    # This should have strict validation and sandboxing in a real application.
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error: Command failed with exit code {e.returncode}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {e}"


# --- Web, Browser, and Resource Tools ---

def _read_url_content_func(url: str) -> str:
    """Reads the textual content from a URL."""
    # Requires 'requests' and 'beautifulsoup4' libraries.
    # pip install requests beautifulsoup4
    return _unimplemented_func(url)

def _search_web_func(query: str) -> str:
    """Performs a web search and returns a summary of results."""
    # Requires a search API (e.g., Google, Bing) or a library like 'duckduckgo-search'.
    return _unimplemented_func(query)

def _open_browser_url_func(url: str) -> str:
    """Opens a URL in the default web browser."""
    try:
        webbrowser.open(url)
        return f"Successfully opened {url} in the browser."
    except Exception as e:
        return f"Error opening URL: {e}"


# --- Tool Definitions ---

# File System
create_file = Tool(
    name="create_file",
    description="Creates a new file at a specified path, optionally with initial content. Fails if the file already exists.",
    func=_create_file_func,
    args_schema=[
        {"name": "file_path", "type": "string", "description": "The path for the new file."},
        {"name": "content", "type": "string", "description": "Optional initial content for the file."}
    ]
)

replace_file_content = Tool(
    name="replace_file_content",
    description="Edits an existing file by completely replacing its content.",
    func=_replace_file_content_func,
    args_schema=[
        {"name": "file_path", "type": "string", "description": "The path to the file to be modified."},
        {"name": "new_content", "type": "string", "description": "The new content to write to the file."}
    ]
)

view_file = Tool(
    name="view_file",
    description="Views the entire contents of a specified file.",
    func=_view_file_func,
    args_schema=[
        {"name": "file_path", "type": "string", "description": "The path to the file to view."}
    ]
)

find_by_name = Tool(
    name="find_by_name",
    description="Searches for files or directories by their exact name within a given directory.",
    func=_find_by_name_func,
    args_schema=[
        {"name": "name", "type": "string", "description": "The file or directory name to search for."},
        {"name": "search_dir", "type": "string", "description": "The directory to start the search from. Defaults to current."}
    ]
)

grep_search = Tool(
    name="grep_search",
    description="Searches for a specific text pattern within files in a directory.",
    func=_grep_search_func,
    args_schema=[
        {"name": "pattern", "type": "string", "description": "The text pattern to search for."},
        {"name": "search_dir", "type": "string", "description": "The directory to search within. Defaults to current."}
    ]
)

list_dir = Tool(
    name="list_dir",
    description="Lists all files and subdirectories within a specified directory.",
    func=_list_dir_func,
    args_schema=[
        {"name": "directory_path", "type": "string", "description": "The path to the directory to list. Defaults to current."}
    ]
)

# Code Analysis
view_code_item = Tool(
    name="view_code_item",
    description="Views a specific code item like a function or class from a source file.",
    func=_view_code_item_func,
    args_schema=[
        {"name": "file_path", "type": "string", "description": "The path to the source code file."},
        {"name": "item_name", "type": "string", "description": "The name of the function or class to view."}
    ]
)

codebase_search = Tool(
    name="codebase_search",
    description="Finds relevant code snippets across the entire codebase using a semantic query.",
    func=_codebase_search_func,
    args_schema=[
        {"name": "query", "type": "string", "description": "A natural language description of the code to find."}
    ]
)

# Command Execution
run_command = Tool(
    name="run_command",
    description="Executes a shell command. SECURITY: This tool is powerful and can be dangerous. Use with caution.",
    func=_run_command_func,
    args_schema=[
        {"name": "command", "type": "string", "description": "The command to execute."}
    ]
)

# Web & Browser
read_url_content = Tool(
    name="read_url_content",
    description="Reads the primary textual content from a given URL.",
    func=_read_url_content_func,
    args_schema=[
        {"name": "url", "type": "string", "description": "The URL to read content from."}
    ]
)

search_web = Tool(
    name="search_web",
    description="Performs a web search and returns a list of results.",
    func=_search_web_func,
    args_schema=[
        {"name": "query", "type": "string", "description": "The search query."}
    ]
)

open_browser_url = Tool(
    name="open_browser_url",
    description="Opens a specified URL in the user's default web browser.",
    func=_open_browser_url_func,
    args_schema=[
        {"name": "url", "type": "string", "description": "The URL to open."}
    ]
)

# A list containing all the new tools for easy registration
all_new_tools: List[Tool] = [
    create_file,
    replace_file_content,
    view_file,
    find_by_name,
    grep_search,
    list_dir,
    view_code_item,
    codebase_search,
    run_command,
    read_url_content,
    search_web,
    open_browser_url,
]
