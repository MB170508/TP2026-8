"""Reusable history display components."""

import flet as ft
from ui.components.colors import OVERLAY_BACKGROUND, CARD_BACKGROUND


def create_history_container(
    item_text: str, item_description: str = "", use_overlay: bool = True
) -> ft.Container:
    """Create a styled history item container.

    Args:
        item_text: Primary text to display
        item_description: Optional secondary/detail text
        use_overlay: If True, use OVERLAY_BACKGROUND; else use CARD_BACKGROUND

    Returns:
        Styled ft.Container for history items
    """
    controls = [ft.Text(item_text, size=12, weight=ft.FontWeight.W_600)]

    if item_description:
        controls.append(ft.Text(item_description, size=10, color=ft.Colors.GREY))

    return ft.Container(
        content=ft.Column(controls, spacing=2),
        padding=6,
        border_radius=4,
        bgcolor=OVERLAY_BACKGROUND if use_overlay else CARD_BACKGROUND,
    )


def create_history_column(max_height: int = 300) -> ft.Column:
    """Create a scrollable history display column.

    Args:
        max_height: Maximum height in pixels (default 300)

    Returns:
        Empty scrollable ft.Column ready for history items
    """
    return ft.Column(
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        height=max_height,
    )
