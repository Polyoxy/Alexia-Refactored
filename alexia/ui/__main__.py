# -*- coding: utf-8 -*-
"""
Main entry point for the Alexia AI assistant application.

This script initializes the configuration, sets up the Ollama client,
and starts the interactive chat session.
"""

import asyncio
import argparse
import os
import sys

from rich.console import Console

from alexia.core.config import Config
from alexia.core.session import ChatSession
from alexia.services.ollama_client import OllamaClient, OllamaError
from alexia.ui.display import display_welcome_banner, display_error, display_info

async def main():
    """Initializes and runs the chat session."""
    parser = argparse.ArgumentParser(description="Alexia - Agentic AI Assistant")
    parser.add_argument("--host", type=str, default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"), help="Ollama host URL")
    parser.add_argument("--model", type=str, default=os.environ.get("OLLAMA_MODEL"), help="Default AI model to use")
    parser.add_argument("--system", type=str, help="Path to a custom system prompt file")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress the startup banner")
    args = parser.parse_args()

    console = Console()

    try:
        # Simplified config handling to prevent previous errors
        config = Config(
            host=args.host,
            model=args.model,
            system_prompt=args.system,
            quiet_mode=args.quiet
        )

        if not config.quiet_mode:
            display_welcome_banner(console, config.model or "Not Specified")

        # Use the async context manager for the client
        async with OllamaClient(host=config.host) as client:
            display_info(console, f"Checking connection to Ollama at {config.host}...")
            
            # Use the correct health_check method
            if not await client.health_check():
                display_error(console, f"Could not connect to Ollama at {config.host}. Please ensure it is running and accessible.")
                return

            display_info(console, "Connection successful.")
            
            if not config.model:
                display_error(console, "No model specified. Please set the OLLAMA_MODEL environment variable or use the --model argument.")
                return

            session = ChatSession(config, client, console)
            await session.run()

    except OllamaError as e:
        display_error(console, str(e))
        sys.exit(1)
    except Exception as e:
        display_error(console, f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
