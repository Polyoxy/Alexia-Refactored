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
