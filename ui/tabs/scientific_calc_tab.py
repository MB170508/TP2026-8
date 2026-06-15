"""Scientific Calculator tab."""

import flet as ft
from managers.ScientificCalculator import ScientificCalculator
from ui.components.colors import ERROR_COLOR, BLUE_COLOR
from ui.components.factories import btn, section, sub


def create_scientific_calc_tab(page: ft.Page) -> ft.Column:
    """Create Scientific Calculator tab.

    Evaluate mathematical expressions with trigonometric, exponential,
    and other functions. Shows available functions, examples, and history.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete scientific calculator tab UI
    """
    # ── Initialize ──────────────────────────────────
    sci_calc = ScientificCalculator()
    sci_input = ft.TextField(label="Expression", width=300, content_padding=8)
    sci_result = ft.Text("", size=16, weight=ft.FontWeight.W_500)
    sci_error = ft.Text("", size=12, color=ERROR_COLOR)
    sci_functions_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    sci_examples_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    sci_history_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    # ── Event Handlers ──────────────────────────────
    def sci_evaluate(e):
        """Evaluate mathematical expression."""
        sci_error.value = ""
        sci_result.value = ""
        expr = sci_input.value.strip()
        if not expr:
            sci_error.value = "Enter an expression."
            page.update()
            return

        result = sci_calc.evaluate_expression(expr)
        if result["success"]:
            sci_result.value = result["message"]
            sci_input.value = ""
            update_sci_history()
        else:
            sci_error.value = result["message"]
        page.update()

    def update_sci_functions():
        """Update available functions display."""
        sci_functions_display.controls.clear()
        functions_result = sci_calc.get_available_functions()
        if functions_result["success"]:
            functions = functions_result["functions"]
            # Filter out private functions
            math_funcs = [f for f in functions if not f.startswith("_")]
            sci_functions_display.controls.append(
                ft.Text(
                    "Available functions:", size=13, weight=ft.FontWeight.W_600
                )
            )
            sci_functions_display.controls.append(
                ft.Text(", ".join(math_funcs), size=12, selectable=True)
            )
        page.update()

    def update_sci_examples():
        """Update examples display."""
        sci_examples_display.controls.clear()
        examples_result = sci_calc.get_examples()
        if examples_result["success"]:
            sci_examples_display.controls.append(
                ft.Text("Examples:", size=13, weight=ft.FontWeight.W_600)
            )
            for example in examples_result["examples"]:
                sci_examples_display.controls.append(
                    ft.Text(example, size=12, selectable=True, color=BLUE_COLOR)
                )
        page.update()

    def update_sci_history():
        """Update calculation history display."""
        sci_history_display.controls.clear()
        history_result = sci_calc.get_history()
        if history_result["success"] and history_result["history"]:
            sci_history_display.controls.append(
                ft.Text(
                    "Recent calculations:", size=13, weight=ft.FontWeight.W_600
                )
            )
            for item in history_result["history"]:
                sci_history_display.controls.append(
                    ft.Text(
                        f"{item['expression']} = {item['result']}", size=12
                    )
                )
        page.update()

    def sci_clear_history(e):
        """Clear calculation history."""
        result = sci_calc.clear_history()
        if result["success"]:
            update_sci_history()
        page.update()

    # Initialize displays
    update_sci_functions()
    update_sci_examples()
    update_sci_history()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Scientific Calculator"),
            sub(
                "Evaluate mathematical expressions with trigonometric, exponential, and other functions."
            ),
            ft.Row([sci_input, btn("Calculate", sci_evaluate, primary=True)]),
            sci_error,
            sci_result,
            ft.Divider(),
            ft.Row(
                [
                    ft.Column(
                        [
                            section("Functions"),
                            ft.Container(
                                content=sci_functions_display, height=150
                            ),
                        ],
                        expand=1,
                    ),
                    ft.VerticalDivider(),
                    ft.Column(
                        [
                            section("Examples"),
                            ft.Container(
                                content=sci_examples_display, height=150
                            ),
                        ],
                        expand=1,
                    ),
                    ft.VerticalDivider(),
                    ft.Column(
                        [
                            section("History"),
                            ft.Container(
                                content=sci_history_display, height=150
                            ),
                            btn("Clear History", sci_clear_history),
                        ],
                        expand=1,
                    ),
                ],
                expand=True,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
