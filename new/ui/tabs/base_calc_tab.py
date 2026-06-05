"""Multi-Base Calculator tab."""

import flet as ft
from MultiBaseConverter import convert
from MultiBaseCalc import MultiBaseCalculator
from utilities.validators import validate_positive_integer
from ui.components.colors import (
    ERROR_COLOR,
    PRIMARY_COLOR,
    GREY_TEXT_COLOR,
    OVERLAY_BACKGROUND,
)
from ui.components.factories import btn, section, sub


def create_base_calc_tab(page: ft.Page) -> ft.Column:
    """Create Multi-Base Calculator tab.

    Converts between binary, octal, decimal, and hexadecimal.
    Evaluates expressions with mixed-base numbers.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete base calculator tab UI
    """
    # ── Initialize ──────────────────────────────────
    multi_base_calc = MultiBaseCalculator()
    base_error = ft.Text("", size=12, color=ERROR_COLOR)
    base_results = ft.Column(spacing=6)
    base_value_input = ft.TextField(label="Value", width=160, content_padding=8)
    base_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("2"),
            ft.dropdown.Option("8"),
            ft.dropdown.Option("10"),
            ft.dropdown.Option("16"),
        ],
        value="10",
        width=100,
        label="From Base",
        content_padding=8,
    )
    expr_input = ft.TextField(
        label="Equation (e.g. 0b1010 + 0xFF)", width=300, content_padding=8
    )
    expr_results = ft.Column(spacing=6)
    history_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    # ── Event Handlers ──────────────────────────────
    def convert_base(e):
        """Convert value between number bases."""
        base_results.controls.clear()
        base_error.value = ""
        result = convert(base_value_input.value, int(base_dropdown.value))
        if not result["success"]:
            base_error.value = result["message"]
            page.update()
            return
        for name, val in result["results"].items():
            base_results.controls.append(
                ft.Row(
                    [
                        ft.Text(f"{name}:", width=100, weight=ft.FontWeight.W_600),
                        ft.Text(val, size=14),
                    ],
                    spacing=8,
                )
            )
        page.update()

    def eval_base_expr(e):
        """Evaluate expression with mixed-base numbers."""
        expr_results.controls.clear()
        base_error.value = ""
        result = multi_base_calc.evaluate_expression(expr_input.value)
        if not result["success"]:
            base_error.value = result["message"]
            page.update()
            return
        expr_results.controls.append(
            ft.Text(
                f"Result: {result['results']['Decimal']}",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY_COLOR,
            )
        )
        for name, val in result["results"].items():
            prefix = {"Binary": "0b", "Octal": "0o", "Hexadecimal": "0x"}.get(
                name, ""
            )
            expr_results.controls.append(
                ft.Row(
                    [
                        ft.Text(f"{name}:", width=100, weight=ft.FontWeight.W_600),
                        ft.Text(f"{prefix}{val}", size=14),
                    ],
                    spacing=8,
                )
            )
        update_history_display()
        page.update()

    def update_history_display():
        """Update history display with recent calculations."""
        history_display.controls.clear()
        history = multi_base_calc.get_history()
        if history:
            history_display.controls.append(
                ft.Text("Recent Calculations:", weight=ft.FontWeight.W_600)
            )
            for item in reversed(history[-5:]):  # Show last 5
                history_display.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"{item['expression']} = {item['results']['Decimal']}",
                                    size=12,
                                ),
                                ft.Text(
                                    f"0b{item['results']['Binary']} | 0o{item['results']['Octal']} | 0x{item['results']['Hexadecimal']}",
                                    size=10,
                                    color=GREY_TEXT_COLOR,
                                ),
                            ],
                            spacing=2,
                        ),
                        padding=6,
                        border_radius=4,
                        bgcolor=OVERLAY_BACKGROUND,
                    )
                )

    def reset_base(e):
        """Reset calculator to initial state."""
        base_value_input.value = ""
        base_results.controls.clear()
        expr_input.value = ""
        expr_results.controls.clear()
        base_error.value = ""
        multi_base_calc.clear_history()
        update_history_display()
        page.update()

    def load_examples(e):
        """Load examples (placeholder)."""
        # Could show examples in a dialog, but for now just pass
        pass

    # Initialize history display
    update_history_display()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Multi-Base Calculator"),
            ft.Row([base_value_input, base_dropdown, btn("Convert", convert_base)]),
            base_results,
            ft.Divider(),
            sub(
                "Equation evaluator with mixed-base numbers (0b, 0o, 0x prefixes)."
            ),
            ft.Row([expr_input, btn("Evaluate", eval_base_expr, primary=True)]),
            expr_results,
            ft.Divider(),
            ft.Container(content=history_display, height=120),
            ft.Row([btn("Reset", reset_base), btn("Examples", load_examples)]),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
