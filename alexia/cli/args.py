# -*- coding: utf-8 -*-
"""
Handles command-line argument parsing for the Alexia application.
"""

import argparse

def parse_args() -> argparse.Namespace:
    """
    Defines and parses command-line arguments for the application.

    Returns:
        argparse.Namespace: An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="A professional, high-performance terminal interface for Ollama.",
        epilog="Example: alexia --model llama3:latest --system \"You are a helpful assistant.\""
    )

    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:11434",
        help="Specifies the Ollama host URL (default: http://localhost:11434)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gemma3n:e4b",
        help="Sets the default model to use on startup (default: gemma3n:e4b)"
    )

    parser.add_argument(
        "--system",
        type=str,
        default=None,
        help="Sets a custom system prompt to use for the session."
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppresses the startup banner and other informational messages."
    )

    return parser.parse_args()

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppresses the startup banner for a quieter launch."
    )

    return parser.parse_args()
