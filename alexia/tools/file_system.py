# -*- coding: utf-8 -*-
"""
Provides agentic tools for interacting with the local file system.
"""

import os
from alexia.tools.tool import Tool

def _read_file_func(file_path: str) -> str:
    """The actual implementation of the file reading logic."""
    try:
        expanded_path = os.path.expanduser(file_path)
        if not os.path.exists(expanded_path):
            return f"Error: File not found at '{expanded_path}'."
        if not os.path.isfile(expanded_path):
            return f"Error: Path '{expanded_path}' is a directory, not a file."
        with open(expanded_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

def _write_file_func(file_path: str, content: str) -> str:
    """The actual implementation of the file writing logic."""
    try:
        expanded_path = os.path.expanduser(file_path)
        dir_path = os.path.dirname(expanded_path)
        
        # Create directory if it doesn't exist
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
        with open(expanded_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to file at '{expanded_path}'"
    except Exception as e:
        return f"Error: Failed to write to file: {e}"

read_file_tool = Tool(
    name="read_file",
    description="Reads the entire content of a specified file. Use this when the user asks to open, read, summarize, or view a file.",
    func=_read_file_func,
    args_schema=[
        {
            "name": "file_path",
            "type": "string",
            "description": "The absolute or relative path to the file."
        }
    ]
)

write_file_tool = Tool(
    name="write_file",
    description="Writes content to a specified file. Creates the file and any necessary directories if they don't exist.",
    func=_write_file_func,
    args_schema=[
        {
            "name": "file_path",
            "type": "string",
            "description": "The absolute or relative path to the file."
        },
        {
            "name": "content",
            "type": "string",
            "description": "The content to write to the file."
        }
    ]
)
