"""UI widget factories for consistent styling across tabs."""

import flet as ft
from ui.components.colors import (
    PRIMARY_COLOR,
    SURFACE_COLOR,
    ON_PRIMARY_COLOR,
    ON_SURFACE_COLOR,
    GREY_COLOR,
)


def btn(label: str, on_click, primary: bool = False) -> ft.Button:
    """Create a styled button with consistent appearance.

    Args:
        label: Button text
        on_click: Click handler function
        primary: If True, use primary color; if False, use surface color

    Returns:
        Styled ft.Button instance
    """
    return ft.Button(
        content=ft.Text(label, size=12),
        style=ft.ButtonStyle(
            bgcolor=PRIMARY_COLOR if primary else SURFACE_COLOR,
            color=ON_PRIMARY_COLOR if primary else ON_SURFACE_COLOR,
            side=ft.BorderSide(width=1, color=PRIMARY_COLOR) if not primary else None,
        ),
        on_click=on_click,
    )


def section(text: str) -> ft.Text:
    """Create a section header text.

    Args:
        text: Header text

    Returns:
        Styled ft.Text for section headers (size 18, bold)
    """
    return ft.Text(text, size=18, weight=ft.FontWeight.W_600)


def sub(text: str) -> ft.Text:
    """Create a subtitle/subheading text.

    Args:
        text: Subtitle text

    Returns:
        Styled ft.Text for subtitles (size 12, grey)
    """
    return ft.Text(text, size=12, color=GREY_COLOR)
