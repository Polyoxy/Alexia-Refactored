# -*- coding: utf-8 -*-
"""
Defines the configuration structure for the Alexia application.
"""

from dataclasses import dataclass
import argparse

@dataclass(frozen=True)
class Config:
    """
    A frozen dataclass to hold all application configuration settings.

    This object is created from the parsed command-line arguments and serves
    as the single source of truth for configuration throughout the application.
    """
    host: str
    model: str
    system_prompt: str | None
    quiet_mode: bool

def create_config_from_args(args: argparse.Namespace) -> Config:
    """
    Factory function to create a Config object from parsed arguments.

    Args:
        args (argparse.Namespace): The parsed arguments from the command line.

    Returns:
        Config: A validated and immutable configuration object.
    """
    return Config(
        host=args.host,
        model=args.model,
        system_prompt=args.system,
        quiet_mode=args.quiet
    )
