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

def _list_directory_func(directory_path: str, show_hidden: bool = False) -> str:
    """Lists contents of a directory with file details.
    
    Args:
        directory_path: Path to the directory to list
        show_hidden: Whether to show hidden files (starting with .)
        
    Returns:
        str: Formatted string containing directory contents or error message
    """
    try:
        expanded_path = os.path.expanduser(directory_path)
        if not os.path.exists(expanded_path):
            return f"Error: Directory not found at '{expanded_path}'"
            
        if not os.path.isdir(expanded_path):
            return f"Error: '{expanded_path}' is not a directory"
            
        entries = []
        for entry in os.scandir(expanded_path):
            if not show_hidden and entry.name.startswith('.'):
                continue
                
            if entry.is_dir():
                entry_type = "[DIR]"
                entry_size = ""
            else:
                entry_type = "[FILE]"
                entry_size = f"{entry.stat().st_size / 1024:.1f} KB"
                
            entries.append(f"{entry_type} {entry.name:<40} {entry_size}")
            
        if not entries:
            return "No files found" if not show_hidden else "Directory is empty"
            
        # Sort directories first, then files, then by name
        entries.sort(key=lambda x: (not x.startswith('[DIR]'), x.lower()))
        
        # Add header
        result = [f"Contents of {expanded_path}:", "-" * 60]
        result.extend(entries)
        result.append(f"\n{len(entries)} items" + (" (hidden files shown)" if show_hidden else ""))
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

list_directory_tool = Tool(
    name="list_directory",
    description="Lists the contents of a directory. Use this when the user asks to see what's in a folder, list files, or explore a directory.",
    func=_list_directory_func,
    args_schema=[
        {
            "name": "directory_path",
            "type": "string",
            "description": "The path to the directory to list",
            "required": True
        },
        {
            "name": "show_hidden",
            "type": "boolean",
            "description": "Whether to show hidden files (starting with .)",
            "required": False,
            "default": False
        }
    ]
)
