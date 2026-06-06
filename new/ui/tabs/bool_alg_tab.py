"""Boolean Algebra Simplifier tab."""

import flet as ft
from managers.BooleanAlgebra import BooleanAlgebraSimplifier
from utilities.validators import validate_boolean_expression
from ui.components.colors import ERROR_COLOR, SUCCESS_COLOR
from ui.components.factories import btn, section, sub


def create_bool_alg_tab(page: ft.Page) -> ft.Column:
    """Create Boolean Algebra Simplifier tab.

    Simplifies boolean expressions and generates truth tables.
    Supports AND (·), OR (+), NOT (~), XOR (^) operators.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete boolean algebra tab UI
    """
    # ── Initialize ──────────────────────────────────
    bool_simplifier = BooleanAlgebraSimplifier()
    bool_error = ft.Text("", size=12, color=ERROR_COLOR)
    bool_result = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    bool_input = ft.TextField(
        label="Expression (e.g. A·B + ~C)", width=300, content_padding=8
    )
    truth_table_text = ft.Text(
        "", size=10, font_family="monospace", selectable=True
    )

    # ── Event Handlers ──────────────────────────────
    def validate_bool_expression_field(e):
        """Real-time validation for boolean expression."""
        if not e.control.value:
            bool_error.value = ""
        else:
            is_valid, error_msg = validate_boolean_expression(e.control.value)
            bool_error.value = error_msg if not is_valid else ""
        page.update()

    bool_input.on_change = validate_bool_expression_field

    def simplify_bool(e):
        """Simplify boolean expression and show truth table."""
        bool_result.controls.clear()
        bool_error.value = ""
        truth_table_text.value = ""
        expr = bool_input.value.strip()
        if not expr:
            bool_error.value = "Enter a boolean expression."
            page.update()
            return
        result = bool_simplifier.simplify(expr)
        if not result["success"]:
            bool_error.value = result["message"]
            page.update()
            return
        if result["type"] == "tautology":
            bool_result.controls.append(
                ft.Text(result["message"], size=14, color=SUCCESS_COLOR)
            )
            page.update()
            return
        if result["type"] == "contradiction":
            bool_result.controls.append(
                ft.Text(result["message"], size=14, color=ERROR_COLOR)
            )
            page.update()
            return

        bool_result.controls.append(
            ft.Text(
                f"Variables: {', '.join(result['vars'])}",
                size=13,
                weight=ft.FontWeight.W_600,
            )
        )
        bool_result.controls.append(
            ft.Text(f"SOP: {result['sop']}", size=13, selectable=True)
        )
        bool_result.controls.append(
            ft.Text(f"POS: {result['pos']}", size=13, selectable=True)
        )
        bool_result.controls.append(ft.Divider())
        bool_result.controls.append(
            ft.Text("Truth Table:", size=13, weight=ft.FontWeight.W_600)
        )
        truth_table_text.value = bool_simplifier.get_truth_table_text()
        for assignment, res in result["table"]:
            vals = "  ".join(f"{v}={assignment[v]}" for v in result["vars"])
            bool_result.controls.append(
                ft.Row(
                    [
                        ft.Text(vals, size=12),
                        ft.Text(
                            f" → {res}",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=SUCCESS_COLOR if res else ERROR_COLOR,
                        ),
                    ],
                    spacing=8,
                )
            )
        page.update()

    def reset_bool(e):
        """Reset simplifier to initial state."""
        bool_input.value = ""
        bool_result.controls.clear()
        bool_error.value = ""
        truth_table_text.value = ""
        page.update()

    def show_examples_bool(e):
        """Show expression examples (placeholder)."""
        # Could show in a dialog, but for now just pass
        pass

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Boolean Algebra Simplifier"),
            sub("Operators: + (OR), · (AND), ~ (NOT)"),
            ft.Row(
                [
                    bool_input,
                    btn("Analyze", simplify_bool, primary=True),
                    btn("Reset", reset_bool),
                    btn("Examples", show_examples_bool),
                ]
            ),
            bool_error,
            ft.Container(content=bool_result, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
