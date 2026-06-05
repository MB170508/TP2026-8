"""Reusable UI Components for consistent styling and reduced duplication."""

import flet as ft
from .constants import (
    PRIMARY_COLOR, ERROR_COLOR, SUCCESS_COLOR, CARD_BACKGROUND, OVERLAY_BACKGROUND,
    GREY_COLOR, GREY_500_COLOR, GREY_400_COLOR, BLUE_COLOR, ORANGE_COLOR
)


def styled_card(title: str, content: ft.Control, height: int = None) -> ft.Container:
    """Reusable card component with consistent styling.

    Args:
        title: Card title
        content: Content control
        height: Optional fixed height

    Returns:
        Styled container
    """
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR),
            content,
        ], spacing=4),
        padding=8,
        border_radius=8,
        bgcolor=CARD_BACKGROUND,
        height=height,
    )


def error_row(error_widget: ft.Text) -> ft.Row:
    """Reusable error display row with icon.

    Args:
        error_widget: Text widget for error message

    Returns:
        Row with icon and error text
    """
    return ft.Row([
        ft.Icon(ft.Icons.ERROR_OUTLINE, size=16, color=ERROR_COLOR),
        error_widget,
    ], spacing=8)


def info_banner(message: str, icon: str = ft.Icons.INFO, color: str = BLUE_COLOR) -> ft.Container:
    """Reusable info banner.

    Args:
        message: Banner message
        icon: Icon to display
        color: Banner color

    Returns:
        Styled container
    """
    lighter_color = color.replace("FF", "1F") if len(color) == 7 else color
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=18, color=color),
            ft.Text(message, size=12, color=color),
        ], spacing=8),
        padding=8,
        border_radius=4,
        bgcolor=lighter_color,
        border=ft.Border.all(1, color),
    )


def labeled_field(label: str, field: ft.Control) -> ft.Column:
    """Reusable labeled input field.

    Args:
        label: Field label
        field: Input control

    Returns:
        Column with label and field
    """
    return ft.Column([
        ft.Text(label, size=11, color=GREY_COLOR, weight=ft.FontWeight.W_500),
        field,
    ], spacing=2)


def result_box(title: str, content: str, selectable: bool = True) -> ft.Container:
    """Reusable result display box.

    Args:
        title: Result title
        content: Result content
        selectable: Whether text is selectable

    Returns:
        Styled result container
    """
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=12, weight=ft.FontWeight.W_600, color=GREY_COLOR),
            ft.Text(content, size=13, selectable=selectable),
        ], spacing=2),
        padding=8,
        border_radius=4,
        bgcolor=OVERLAY_BACKGROUND,
        border=ft.Border.all(1, GREY_400_COLOR),
    )


def history_item(query: str, result: str, on_click=None) -> ft.Container:
    """Reusable history item.

    Args:
        query: Query text
        result: Result text
        on_click: Click handler

    Returns:
        Styled container
    """
    return ft.Container(
        content=ft.Column([
            ft.Text(query, size=11, weight=ft.FontWeight.W_600),
            ft.Text(result, size=10, color=GREY_500_COLOR),
        ], spacing=2),
        padding=6,
        border_radius=4,
        bgcolor=OVERLAY_BACKGROUND,
        on_click=on_click,
    )


def spinner_overlay(message: str = "Loading...") -> ft.Container:
    """Loading spinner overlay.

    Args:
        message: Loading message

    Returns:
        Centered loading container
    """
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=2),
            ft.Text(message, size=12),
        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment.center,
    )


def success_banner(message: str) -> ft.Container:
    """Success message banner.

    Args:
        message: Success message

    Returns:
        Styled success container
    """
    return info_banner(message, icon=ft.Icons.CHECK_CIRCLE, color=SUCCESS_COLOR)


def warning_banner(message: str) -> ft.Container:
    """Warning message banner.

    Args:
        message: Warning message

    Returns:
        Styled warning container
    """
    return info_banner(message, icon=ft.Icons.WARNING, color=ORANGE_COLOR)
