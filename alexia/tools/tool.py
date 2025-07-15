# -*- coding: utf-8 -*-
"""
Defines the core Tool class for creating agentic tools.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List

@dataclass
class Tool:
    """Represents an agentic tool that the AI can use.

    Attributes:
        name (str): The name of the tool.
        description (str): A detailed description of what the tool does.
        func (Callable): The actual function to execute.
        args_schema (List[Dict[str, Any]]): A schema defining the arguments,
            their types, and descriptions. This helps the AI understand how
            to use the tool.
    """
    name: str
    description: str
    func: Callable
    args_schema: List[Dict[str, Any]] = field(default_factory=list)

    def to_prompt_string(self) -> str:
        """Generates a string representation of the tool for the AI's prompt."""
        schema_str = ', '.join([f'{arg["name"]}: {arg["type"]}' for arg in self.args_schema])
        return f'- {self.name}({schema_str}): {self.description}'
