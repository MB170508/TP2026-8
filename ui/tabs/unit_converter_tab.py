"""Unit Converter tab."""

import flet as ft
from managers.UnitConverter import UnitConverter
from utilities.validators import validate_float
from ui.components.colors import (
    ERROR_COLOR,
    PRIMARY_COLOR,
    ON_SURFACE_COLOR,
    OVERLAY_BACKGROUND,
)
from ui.components.factories import btn, section


def create_unit_converter_tab(page: ft.Page) -> ft.Column:
    """Create Unit Converter tab.

    Converts between various units across multiple categories
    (length, weight, temperature, etc.).

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete unit converter tab UI
    """
    # ── Initialize ──────────────────────────────────
    unit_converter = UnitConverter()
    unit_error = ft.Text("", size=12, color=ERROR_COLOR)
    unit_results = ft.Column(spacing=4)
    unit_history = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    unit_categories_dd = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in unit_converter.get_categories()],
        value=unit_converter.get_categories()[0],
        width=160,
        label="Category",
        content_padding=8,
        on_select=lambda e: on_category_change(e),
    )
    unit_from = ft.Dropdown(label="From", width=140, content_padding=8)
    unit_to = ft.Dropdown(label="To", width=140, content_padding=8)
    unit_value = ft.TextField(
        label="Value",
        width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=8,
    )

    # ── Event Handlers ──────────────────────────────
    def validate_unit_value(e):
        """Real-time validation for conversion value."""
        if not e.control.value:
            unit_error.value = ""
        else:
            is_valid, error_msg = validate_float(e.control.value, min_val=0)
            unit_error.value = error_msg if not is_valid else ""
        page.update()

    unit_value.on_change = validate_unit_value

    def on_category_change(e):
        """Handle category dropdown change."""
        category = e.data if e and e.data else unit_converter.current_category
        result = unit_converter.set_category(category)
        if not result["success"]:
            unit_error.value = result["message"]
            page.update()
            return

        units = unit_converter.get_units_for_category(category)
        unit_from.options.clear()
        unit_to.options.clear()
        for u in units:
            unit_from.options.append(ft.dropdown.Option(u))
            unit_to.options.append(ft.dropdown.Option(u))
        if units:
            unit_from.value = units[0]
            unit_to.value = units[1] if len(units) > 1 else units[0]
        else:
            unit_from.value = None
            unit_to.value = None
        unit_results.controls.clear()
        unit_value.value = ""
        page.update()

    def convert_unit(e):
        """Convert value between selected units."""
        unit_results.controls.clear()
        unit_error.value = ""
        try:
            val = float(unit_value.value)
        except (ValueError, TypeError):
            unit_error.value = "Enter a valid number."
            page.update()
            return

        if unit_from.value == unit_to.value:
            unit_error.value = "Select different units."
            page.update()
            return

        result = unit_converter.convert_value(val, unit_from.value, unit_to.value)
        if not result["success"]:
            unit_error.value = result["message"]
            page.update()
            return

        unit_results.controls.append(
            ft.Text(
                f"{val} {unit_from.value} = {result['value']:.6g} {unit_to.value}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY_COLOR,
            )
        )
        update_unit_history()
        page.update()

    def convert_to_all_units(e):
        """Convert to all units in current category."""
        unit_results.controls.clear()
        unit_error.value = ""
        try:
            val = float(unit_value.value)
        except (ValueError, TypeError):
            unit_error.value = "Enter a valid number."
            page.update()
            return

        result = unit_converter.convert_to_all(val, unit_from.value)
        if not result["success"]:
            unit_error.value = result["message"]
            page.update()
            return

        for name, v in result["results"].items():
            color = PRIMARY_COLOR if name == unit_from.value else ON_SURFACE_COLOR
            weight = (
                ft.FontWeight.W_600 if name == unit_from.value else ft.FontWeight.W_400
            )
            unit_results.controls.append(
                ft.Row(
                    [
                        ft.Text(f"{name}:", width=90, weight=weight, color=color),
                        ft.Text(f"{v:.6g}", size=13),
                    ],
                    spacing=8,
                )
            )
        update_unit_history()
        page.update()

    def update_unit_history():
        """Update history display with recent conversions."""
        unit_history.controls.clear()
        history = unit_converter.get_history()
        if history:
            unit_history.controls.append(
                ft.Text("Recent Conversions:", weight=ft.FontWeight.W_600)
            )
            for item in reversed(history[-5:]):  # Show last 5
                unit_history.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"{item['value']} {item['from_unit']} → {item['result']:.4g} {item['to_unit']}",
                            size=12,
                        ),
                        padding=6,
                        border_radius=4,
                        bgcolor=OVERLAY_BACKGROUND,
                    )
                )

    def reset_unit(e):
        """Reset converter to initial state."""
        unit_value.value = ""
        unit_results.controls.clear()
        unit_error.value = ""
        unit_converter.clear_history()
        update_unit_history()
        page.update()

    # Initialize units for default category
    on_category_change(None)
    update_unit_history()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Unit Converter"),
            ft.Row([unit_categories_dd]),
            ft.Row(
                [
                    unit_from,
                    unit_to,
                    unit_value,
                    btn("Convert", convert_unit, primary=True),
                    btn("Show All", convert_to_all_units),
                    btn("Reset", reset_unit),
                ]
            ),
            unit_error,
            ft.Container(content=unit_results, expand=True),
            ft.Container(content=unit_history, height=120),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
