"""Error display utilities for consistent error handling."""

import flet as ft
from ui.components.colors import ERROR_COLOR


def create_error_widget() -> ft.Text:
    """Create a new error display widget.

    Returns:
        Empty ft.Text widget configured for error messages
    """
    return ft.Text("", size=12, color=ERROR_COLOR)


def set_error(
    error_widget: ft.Text,
    message: str,
    color: str = ERROR_COLOR,
    page: ft.Page = None,
) -> None:
    """Set error message on widget and optionally update page.

    Args:
        error_widget: ft.Text widget to display error in
        message: Error message text
        color: Text color (default: ERROR_COLOR)
        page: Optional page instance to call update() on
    """
    error_widget.value = message
    error_widget.color = color
    if page:
        page.update()
