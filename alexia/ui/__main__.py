# -*- coding: utf-8 -*-
"""
This module serves as the main entry point for the Alexia application.

It orchestrates the startup process, including parsing command-line arguments,
creating a configuration object, and initializing the main application components.
"""
import sys
import asyncio
from rich.console import Console

from alexia.cli.args import parse_args
from alexia.core.config import Config, create_config_from_args
from alexia.services.ollama_client import OllamaClient, OllamaError
from alexia.ui.display import display_welcome_banner, display_models_table, display_error, display_info
from alexia.core.session import ChatSession

async def main():
    """Main entry point for the Alexia application."""
    args = parse_args()
    config = create_config_from_args(args)
    console = Console()

    if not config.quiet_mode:
        display_welcome_banner(console, config.model)

    try:
        async with OllamaClient(host=config.host) as client:
            display_info(console, f"Checking connection to Ollama at {config.host}...")

            if not await client.health_check():
                display_error(console, f"Could not connect to Ollama at {config.host}. Please ensure it is running and accessible.")
                return

            display_info(console, "Connection successful. Fetching models...")
            
            # The startup process is complete, now start the chat session.
            session = ChatSession(config, client, console)
            await session.run()

    except OllamaError as e:
        display_error(console, str(e))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
