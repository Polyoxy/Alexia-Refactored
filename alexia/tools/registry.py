# -*- coding: utf-8 -*-
"""
Manages the collection of agentic tools available to the AI.
"""

from typing import List, Dict, Optional

from alexia.tools.tool import Tool

class ToolRegistry:
    """A registry to hold and manage all available agentic tools."""

    def __init__(self, tools: List[Tool] = None):
        self._tools: Dict[str, Tool] = {tool.name: tool for tool in tools} if tools else {}

    def register(self, tool: Tool):
        """Registers a new tool."""
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieves a tool by its name."""
        return self._tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """Returns a list of all registered tools."""
        return list(self._tools.values())

    def generate_prompt_string(self) -> str:
        """Generates a string for the system prompt describing all tools."""
        if not self._tools:
            return "" # No tools available.

        header = (
            "You have access to the following tools. When you need to use a tool, "
            "respond ONLY with a single JSON object with two keys: 'tool_name' and 'arguments'.\n"
            "The 'arguments' key should contain an object with the required parameters.\n\n"
            "Available Tools:\n"
        )

        tool_descriptions = [tool.to_prompt_string() for tool in self.get_all_tools()]
        return header + "\n".join(tool_descriptions)
