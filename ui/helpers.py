"""UI Helpers - Reusable UI functions."""

import flet as ft
from .constants import PRIMARY_COLOR, SURFACE_COLOR, ON_PRIMARY_COLOR, ON_SURFACE_COLOR, ERROR_COLOR, GREY_COLOR


def btn(label: str, on_click, primary: bool = False) -> ft.Button:
    """Create a styled button.

    Args:
        label: Button text
        on_click: Click handler
        primary: Whether button is primary style

    Returns:
        Styled button control
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
    """Create a section header.

    Args:
        text: Header text

    Returns:
        Styled text control
    """
    return ft.Text(text, size=18, weight=ft.FontWeight.W_600)


def sub(text: str) -> ft.Text:
    """Create a subtitle.

    Args:
        text: Subtitle text

    Returns:
        Styled text control
    """
    return ft.Text(text, size=12, color=GREY_COLOR)


def set_error(page: ft.Page, error_widget: ft.Text, message: str, color: str = ERROR_COLOR) -> None:
    """Set error widget text and color, then update page.

    Args:
        page: Flet page for update
        error_widget: Error text widget to update
        message: Error message
        color: Error color (default: ERROR_COLOR)
    """
    error_widget.value = message
    error_widget.color = color
    page.update()
