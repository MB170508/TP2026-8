"""UI Main Entry Point - Orchestrator."""

import asyncio
import flet as ft

# Re-export everything from root main for now
# In future phases, this will import individual tab modules
from __main__ import main as original_main


def main(page: ft.Page):
    """Application entry point."""
    original_main(page)


if __name__ == "__main__":
    ft.run(main)
