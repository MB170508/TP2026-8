import flet as ft
from Calculator import calculate_weighted_average
from IPv4Subnetting import SubnetCalculator
from MultiBaseConverter import convert
from MultiBaseCalc import MultiBaseCalculator
from UnitConverter import UnitConverter
from BooleanAlgebra import BooleanAlgebraSimplifier
from ScientificCalculator import ScientificCalculator
from Flashcards import FlashcardManager
from Notes import NotesManager
from EduPage import EduSession, EduPageManager, save_credentials, load_credentials, clear_credentials
from Lunch import LunchMenuManager
from WolframAlpha import WolframAlphaManager

# ── Constants ──────────────────────────────────────────────────
CARD_BACKGROUND = "#1F000000"
PRIMARY_COLOR = ft.Colors.PRIMARY
ERROR_COLOR = ft.Colors.RED
SUCCESS_COLOR = ft.Colors.GREEN
GREY_COLOR = ft.Colors.GREY_600
GREY_TEXT_COLOR = ft.Colors.GREY
GREY_500_COLOR = ft.Colors.GREY_500
GREY_300_COLOR = ft.Colors.GREY_300
GREY_400_COLOR = ft.Colors.GREY_400
BLUE_COLOR = ft.Colors.BLUE
BLUE_300_COLOR = ft.Colors.BLUE_300
TEAL_COLOR = ft.Colors.TEAL
SURFACE_COLOR = ft.Colors.SURFACE
ON_PRIMARY_COLOR = ft.Colors.ON_PRIMARY
ON_SURFACE_COLOR = ft.Colors.ON_SURFACE
ORANGE_COLOR = ft.Colors.ORANGE
BROWN_COLOR = ft.Colors.BROWN
GREEN_700_COLOR = ft.Colors.GREEN_700
AMBER_COLOR = ft.Colors.AMBER
SECONDARY_COLOR = ft.Colors.SECONDARY


def main(page: ft.Page):
    page.title = "IT Toolbox"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 12
    page.spacing = 8
    page.window_width = 1100
    page.window_height = 850

    # ── Theme mode toggle ──
    _mode_cycle = [ft.ThemeMode.SYSTEM]  # cycle: SYSTEM -> LIGHT -> DARK -> SYSTEM

    def toggle_theme(e):
        order = [ft.ThemeMode.SYSTEM, ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]
        idx = (order.index(_mode_cycle[0]) + 1) % 3
        _mode_cycle[0] = order[idx]
        page.theme_mode = order[idx]
        icon_map = {
            ft.ThemeMode.SYSTEM: ft.Icons.BRIGHTNESS_AUTO,
            ft.ThemeMode.LIGHT: ft.Icons.LIGHT_MODE,
            ft.ThemeMode.DARK: ft.Icons.DARK_MODE,
        }
        theme_icon.icon = icon_map[order[idx]]
        page.update()

    theme_icon = ft.IconButton(icon=ft.Icons.BRIGHTNESS_AUTO, on_click=toggle_theme)

    header = ft.Row(
        [
            ft.Text("IT Toolbox", size=30, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            theme_icon,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    def btn(label, on_click, primary=False):
        return ft.Button(
            content=ft.Text(label, size=12),
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_COLOR if primary else SURFACE_COLOR,
                color=ON_PRIMARY_COLOR if primary else ON_SURFACE_COLOR,
                side=ft.BorderSide(width=1, color=PRIMARY_COLOR) if not primary else None,
            ),
            on_click=on_click,
        )

    def section(text):
        return ft.Text(text, size=18, weight=ft.FontWeight.W_600)

    def sub(text):
        return ft.Text(text, size=12, color=GREY_COLOR)

    # ═══════════════════════════════════════════════════════
    # TAB 0: IPv4 Subnet Calculator
    # ═══════════════════════════════════════════════════════
    subnet_calculator = SubnetCalculator()
    subnet_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    subnet_error = ft.Text("", size=12, color=ERROR_COLOR)
    subnet_result_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    network_input = ft.TextField(label="Network (e.g. 192.168.10.0/24)", width=280, content_padding=8)
    segment_input = ft.TextField(label="Users", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)

    def build_segments():
        subnet_display.controls.clear()
        segments = subnet_calculator.get_segments()["segments"]
        for i, u in enumerate(segments):
            subnet_display.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.ROUTER, size=14, color=BLUE_COLOR),
                    ft.Text(f"Segment {i+1}: {u} users", size=13),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=14,
                        on_click=lambda e, idx=i: remove_segment(idx),
                    ),
                ], spacing=8)
            )

    def add_segment(e):
        subnet_error.value = ""
        result = subnet_calculator.add_segment(segment_input.value)
        if result["success"]:
            segment_input.value = ""
            build_segments()
            subnet_result_col.controls.clear()
        else:
            subnet_error.value = result["message"]
        page.update()

    def remove_segment(idx):
        result = subnet_calculator.remove_segment(idx)
        if result["success"]:
            build_segments()
            subnet_result_col.controls.clear()
        else:
            subnet_error.value = result["message"]
        page.update()

    def calc_subnet(e):
        subnet_result_col.controls.clear()
        result = subnet_calculator.calculate_subnets(network_input.value)
        if not result["success"]:
            subnet_result_col.controls.append(ft.Text(result["message"], size=13, color=ERROR_COLOR))
            page.update()
            return

        subnet_result_col.controls.append(
            ft.Text(f"Base: {result['base_address']}  |  Total IPs: {result['total_ips']}",
                    size=13, weight=ft.FontWeight.W_600)
        )
        for i, s in enumerate(result["subnets"], 1):
            range_str = f"{s['FirstUsable']} - {s['LastUsable']}" if s['usable'] > 0 else "N/A"
            subnet_result_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Seg {i} — {s['users']} users", size=13, weight=ft.FontWeight.W_600),
                        ft.Text(f"Network: {s['network']}/{s['cidr']}  |  Mask: {s['mask']}", size=12),
                        ft.Text(f"Usable: {range_str} ({s['usable']} hosts)", size=12),
                    ], spacing=2),
                    padding=8,
                    border_radius=6,
                    bgcolor="#1F000000",
                )
            )
        page.update()

    def reset_subnet(e):
        result = subnet_calculator.reset()
        build_segments()
        subnet_result_col.controls.clear()
        network_input.value = ""
        segment_input.value = ""
        subnet_error.value = ""
        page.update()

    # Initialize segments display
    build_segments()

    subnet_page_content = ft.Column([
        section("IPv4 Subnet Calculator"),
        sub("VLSM subnetting with custom segment requirements."),
        network_input,
        ft.Row([segment_input, btn("Add Segment", add_segment)]),
        subnet_error,
        ft.Container(content=subnet_display, expand=True),
        ft.Row([btn("Calculate", calc_subnet, primary=True), btn("Reset", reset_subnet)]),
        subnet_result_col,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 1: Multi-Base Calculator
    # ═══════════════════════════════════════════════════════
    multi_base_calc = MultiBaseCalculator()
    base_error = ft.Text("", size=12, color=ERROR_COLOR)
    base_results = ft.Column(spacing=6)
    base_value_input = ft.TextField(label="Value", width=160, content_padding=8)
    base_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("2"), ft.dropdown.Option("8"), ft.dropdown.Option("10"), ft.dropdown.Option("16")],
        value="10", width=100, label="From Base", content_padding=8,
    )
    expr_input = ft.TextField(label="Equation (e.g. 0b1010 + 0xFF)", width=300, content_padding=8)
    expr_results = ft.Column(spacing=6)
    history_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    def convert_base(e):
        base_results.controls.clear()
        base_error.value = ""
        # For now, keep the old convert function - we can refactor this later if needed
        result = convert(base_value_input.value, int(base_dropdown.value))
        if not result["success"]:
            base_error.value = result["message"]
            page.update()
            return
        for name, val in result["results"].items():
            base_results.controls.append(
                ft.Row([ft.Text(f"{name}:", width=100, weight=ft.FontWeight.W_600), ft.Text(val, size=14)], spacing=8)
            )
        page.update()

    def eval_base_expr(e):
        expr_results.controls.clear()
        base_error.value = ""
        result = multi_base_calc.evaluate_expression(expr_input.value)
        if not result["success"]:
            base_error.value = result["message"]
            page.update()
            return
        expr_results.controls.append(ft.Text(f"Result: {result['results']['Decimal']}", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR))
        for name, val in result["results"].items():
            prefix = {"Binary": "0b", "Octal": "0o", "Hexadecimal": "0x"}.get(name, "")
            expr_results.controls.append(
                ft.Row([ft.Text(f"{name}:", width=100, weight=ft.FontWeight.W_600), ft.Text(f"{prefix}{val}", size=14)], spacing=8)
            )
        update_history_display()
        page.update()

    def update_history_display():
        history_display.controls.clear()
        history = multi_base_calc.get_history()
        if history:
            history_display.controls.append(ft.Text("Recent Calculations:", weight=ft.FontWeight.W_600))
            for item in reversed(history[-5:]):  # Show last 5
                history_display.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{item['expression']} = {item['results']['Decimal']}", size=12),
                            ft.Text(f"0b{item['results']['Binary']} | 0o{item['results']['Octal']} | 0x{item['results']['Hexadecimal']}", size=10, color=GREY_TEXT_COLOR),
                        ], spacing=2),
                        padding=6,
                        border_radius=4,
                        bgcolor="#0F000000",
                    )
                )

    def reset_base(e):
        base_value_input.value = ""
        base_results.controls.clear()
        expr_input.value = ""
        expr_results.controls.clear()
        base_error.value = ""
        multi_base_calc.clear_history()
        update_history_display()
        page.update()

    def load_examples(e):
        examples = multi_base_calc.get_examples()
        # Could show examples in a dialog or something, but for now just clear
        pass

    # Initialize history display
    update_history_display()

    base_page_content = ft.Column([
        section("Multi-Base Calculator"),
        ft.Row([base_value_input, base_dropdown, btn("Convert", convert_base)]),
        base_results,
        ft.Divider(),
        sub("Equation evaluator with mixed-base numbers (0b, 0o, 0x prefixes)."),
        ft.Row([expr_input, btn("Evaluate", eval_base_expr, primary=True)]),
        expr_results,
        ft.Divider(),
        ft.Container(content=history_display, height=120),
        ft.Row([btn("Reset", reset_base), btn("Examples", load_examples)]),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 2: Boolean Algebra Simplifier
    # ═══════════════════════════════════════════════════════
    bool_simplifier = BooleanAlgebraSimplifier()
    bool_error = ft.Text("", size=12, color=ERROR_COLOR)
    bool_result = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    bool_input = ft.TextField(label="Expression (e.g. A·B + ~C)", width=300, content_padding=8)
    truth_table_text = ft.Text("", size=10, font_family="monospace", selectable=True)

    def simplify_bool(e):
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
            bool_result.controls.append(ft.Text(result["message"], size=14, color=SUCCESS_COLOR))
            page.update()
            return
        if result["type"] == "contradiction":
            bool_result.controls.append(ft.Text(result["message"], size=14, color=ERROR_COLOR))
            page.update()
            return

        bool_result.controls.append(ft.Text(f"Variables: {', '.join(result['vars'])}", size=13, weight=ft.FontWeight.W_600))
        bool_result.controls.append(ft.Text(f"SOP: {result['sop']}", size=13, selectable=True))
        bool_result.controls.append(ft.Text(f"POS: {result['pos']}", size=13, selectable=True))
        bool_result.controls.append(ft.Divider())
        bool_result.controls.append(ft.Text("Truth Table:", size=13, weight=ft.FontWeight.W_600))
        truth_table_text.value = bool_simplifier.get_truth_table_text()
        for assignment, res in result["table"]:
            vals = "  ".join(f"{v}={assignment[v]}" for v in result["vars"])
            bool_result.controls.append(
                ft.Row([ft.Text(vals, size=12), ft.Text(f" → {res}", size=12, weight=ft.FontWeight.BOLD,
                            color=SUCCESS_COLOR if res else ERROR_COLOR)], spacing=8)
            )
        page.update()

    def reset_bool(e):
        bool_input.value = ""
        bool_result.controls.clear()
        bool_error.value = ""
        truth_table_text.value = ""
        page.update()

    def show_examples_bool(e):
        examples = bool_simplifier.get_examples()
        # Could show in a dialog, but for now just clear
        pass

    bool_page_content = ft.Column([
        section("Boolean Algebra Simplifier"),
        sub("Operators: + (OR), · (AND), ~ (NOT)"),
        ft.Row([bool_input, btn("Analyze", simplify_bool, primary=True), btn("Reset", reset_bool), btn("Examples", show_examples_bool)]),
        bool_error,
        ft.Container(content=bool_result, expand=True),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 3: Unit Converter
    # ═══════════════════════════════════════════════════════
    unit_converter = UnitConverter()
    unit_error = ft.Text("", size=12, color=ERROR_COLOR)
    unit_results = ft.Column(spacing=4)
    unit_history = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    unit_categories_dd = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in unit_converter.get_categories()],
        value=unit_converter.get_categories()[0], width=160, label="Category", content_padding=8,
        on_select=lambda e: on_category_change(e)
    )
    unit_from = ft.Dropdown(label="From", width=140, content_padding=8)
    unit_to = ft.Dropdown(label="To", width=140, content_padding=8)
    unit_value = ft.TextField(label="Value", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)

    def on_category_change(e):
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
            ft.Text(f"{val} {unit_from.value} = {result['value']:.6g} {unit_to.value}",
                    size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
        )
        update_unit_history()
        page.update()

    def convert_to_all_units(e):
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
            weight = ft.FontWeight.W_600 if name == unit_from.value else ft.FontWeight.W_400
            unit_results.controls.append(
                ft.Row([ft.Text(f"{name}:", width=90, weight=weight, color=color), ft.Text(f"{v:.6g}", size=13)], spacing=8)
            )
        update_unit_history()
        page.update()

    def update_unit_history():
        unit_history.controls.clear()
        history = unit_converter.get_history()
        if history:
            unit_history.controls.append(ft.Text("Recent Conversions:", weight=ft.FontWeight.W_600))
            for item in reversed(history[-5:]):  # Show last 5
                unit_history.controls.append(
                    ft.Container(
                        content=ft.Text(f"{item['value']} {item['from_unit']} → {item['result']:.4g} {item['to_unit']}", size=12),
                        padding=6,
                        border_radius=4,
                        bgcolor="#0F000000",
                    )
                )

    def reset_unit(e):
        unit_value.value = ""
        unit_results.controls.clear()
        unit_error.value = ""
        unit_converter.clear_history()
        update_unit_history()
        page.update()

    # Initialize units for default category
    on_category_change(None)
    update_unit_history()

    unit_page_content = ft.Column([
        section("Unit Converter"),
        ft.Row([unit_categories_dd]),
        ft.Row([unit_from, unit_to, unit_value, btn("Convert", convert_unit, primary=True), btn("Show All", convert_to_all_units), btn("Reset", reset_unit)]),
        unit_error,
        ft.Container(content=unit_results, expand=True),
        ft.Container(content=unit_history, height=120),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 4: Flashcards
    # ═══════════════════════════════════════════════════════
    flashcard_manager = FlashcardManager()
    fc_deck_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    fc_deck_selector = ft.Dropdown(label="Select Deck", width=200, content_padding=8)
    fc_new_deck_name = ft.TextField(label="New Deck Name", width=180, content_padding=8)
    fc_card_front = ft.TextField(label="Front", width=180, content_padding=8)
    fc_card_back = ft.TextField(label="Back", width=180, content_padding=8)
    fc_deck_error = ft.Text("", size=12, color=ERROR_COLOR)
    fc_card_display = ft.Column(spacing=8)
    fc_quiz_progress = ft.Text("", size=12)

    def refresh_deck_list():
        fc_deck_list.controls.clear()
        fc_deck_selector.options.clear()
        deck_names = flashcard_manager.get_deck_names()
        for name in deck_names:
            info = flashcard_manager.get_deck_info(name)
            count = info["card_count"]
            fc_deck_list.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.LAYERS, size=14, color=TEAL_COLOR),
                    ft.Text(f"{name} ({count})", size=13),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_size=14, on_click=lambda e, n=name: delete_deck_handler(n)),
                ], spacing=8)
            )
            fc_deck_selector.options.append(ft.dropdown.Option(name))
        if deck_names:
            fc_deck_selector.value = deck_names[0]

    def create_deck_handler(e):
        fc_deck_error.value = ""
        name = fc_new_deck_name.value.strip()
        if not name:
            fc_deck_error.value = "Deck name cannot be empty."
            page.update()
            return
        result = flashcard_manager.create_deck(name)
        if not result["success"]:
            fc_deck_error.value = result["message"]
            page.update()
            return
        fc_new_deck_name.value = ""
        refresh_deck_list()
        page.update()

    def delete_deck_handler(name):
        result = flashcard_manager.delete_deck(name)
        if not result["success"]:
            fc_deck_error.value = result["message"]
        refresh_deck_list()
        fc_card_display.controls.clear()
        fc_quiz_progress.value = ""
        page.update()

    def add_card_handler(e):
        fc_deck_error.value = ""
        deck_name = fc_deck_selector.value
        if not deck_name:
            fc_deck_error.value = "Select or create a deck first."
            page.update()
            return
        front = fc_card_front.value.strip()
        back = fc_card_back.value.strip()
        if not front or not back:
            fc_deck_error.value = "Both front and back are required."
            page.update()
            return
        result = flashcard_manager.add_card(deck_name, front, back)
        if not result["success"]:
            fc_deck_error.value = result["message"]
            page.update()
            return
        fc_card_front.value = ""
        fc_card_back.value = ""
        refresh_deck_list()
        page.update()

    def start_quiz_handler(e):
        fc_card_display.controls.clear()
        fc_deck_error.value = ""
        fc_quiz_progress.value = ""
        deck_name = fc_deck_selector.value
        if not deck_name:
            fc_deck_error.value = "Select a deck first."
            page.update()
            return
        result = flashcard_manager.start_quiz(deck_name)
        if not result["success"]:
            fc_deck_error.value = result["message"]
            page.update()
            return
        show_current_card()

    def show_current_card():
        fc_card_display.controls.clear()
        card_result = flashcard_manager.get_current_card()
        if not card_result["success"]:
            if "completed" in card_result["message"].lower():
                fc_card_display.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🎉 Quiz Complete!", size=20, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR),
                            ft.Text("Great job studying!", size=14),
                            ft.Row([
                                btn("Restart Quiz", restart_quiz_handler),
                                btn("New Quiz", start_quiz_handler)
                            ], spacing=10)
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20, border_radius=10, bgcolor="#1F000000", alignment=ft.alignment.center,
                    )
                )
            else:
                fc_deck_error.value = card_result["message"]
            page.update()
            return

        front_text = card_result["front"]
        back_text = card_result["back"]
        progress = f"{card_result['index']}/{card_result['total']}"
        fc_quiz_progress.value = f"Card {progress}"

        if back_text is None:
            # Show front, allow flip
            fc_card_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Front", size=11, color=GREY_COLOR),
                        ft.Text(front_text, size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Click to reveal answer", size=12, color=GREY_500_COLOR),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20, border_radius=10, bgcolor="#1F000000", alignment=ft.alignment.center,
                )
            )
            fc_card_display.controls.append(
                ft.Row([
                    btn("Flip Card", flip_card_handler, primary=True),
                    btn("Next Card", next_card_handler)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            )
        else:
            # Show both front and back
            fc_card_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Front", size=11, color=GREY_COLOR),
                        ft.Text(front_text, size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Back", size=11, color=GREY_COLOR),
                        ft.Text(back_text, size=16),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20, border_radius=10, bgcolor="#1F000000", alignment=ft.alignment.center,
                )
            )
            fc_card_display.controls.append(
                ft.Row([
                    btn("Next Card", next_card_handler, primary=True),
                    btn("Restart Quiz", restart_quiz_handler)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            )
        page.update()

    def flip_card_handler(e):
        result = flashcard_manager.flip_card()
        if result["success"]:
            show_current_card()

    def next_card_handler(e):
        result = flashcard_manager.next_card()
        if result["success"]:
            show_current_card()
        else:
            show_current_card()  # This will show completion message

    def restart_quiz_handler(e):
        result = flashcard_manager.restart_quiz()
        if result["success"]:
            show_current_card()
        else:
            fc_deck_error.value = result["message"]
            page.update()

    refresh_deck_list()

    fc_page_content = ft.Column([
        section("Flashcards"),
        ft.Row([fc_new_deck_name, btn("Create", create_deck_handler)]),
        ft.Row([fc_card_front, fc_card_back, btn("Add", add_card_handler)]),
        fc_deck_error,
        ft.Row([fc_deck_selector, btn("Quiz", start_quiz_handler, primary=True)]),
        fc_quiz_progress,
        ft.Container(content=fc_deck_list, expand=True),
        fc_card_display,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 5: Notepad with CZ/EN prediction
    # ═══════════════════════════════════════════════════════
    notes_manager = NotesManager()
    notes_list = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
    notes_list_header = ft.Text("Notes", size=13, weight=ft.FontWeight.W_600, visible=False)
    note_title_input = ft.TextField(label="Note title", width=180, content_padding=8)
    editor_frame = ft.Column(scroll=ft.ScrollMode.AUTO)
    note_editor = ft.TextField(
        label="Write...",
        multiline=True,
        min_lines=8,
        expand=True,
    )
    editor_frame.controls.append(note_editor)
    note_lang = ft.Dropdown(
        options=[ft.dropdown.Option("cz"), ft.dropdown.Option("en")],
        value="cz", width=80, label="Lang", content_padding=8,
    )
    predictions_row = ft.Row(spacing=6)
    suggestions_label = ft.Text("Suggestions:", size=11, color=GREY_500_COLOR, visible=False)
    note_error = ft.Text("", size=12, color=ERROR_COLOR)
    note_info = ft.Text("", size=12, color=GREY_500_COLOR)
    note_actions_row = None  # created below after all handlers defined
    note_editor.visible = False

    def refresh_notes_list():
        notes_list.controls.clear()
        all_notes = notes_manager.get_all_notes()
        notes_list_header.visible = len(all_notes) > 0
        for i, n in enumerate(all_notes):
            current = notes_manager.get_current_note()
            is_current = current.get("success") and current["note"]["title"] == n["title"]
            color = PRIMARY_COLOR if is_current else ON_SURFACE_COLOR
            weight = ft.FontWeight.W_600 if is_current else ft.FontWeight.W_400
            notes_list.controls.append(
                ft.ListTile(
                    title=ft.Text(n["title"], size=13, color=color, weight=weight),
                    trailing=ft.IconButton(icon=ft.Icons.DELETE_OUTLINED, icon_size=16, on_click=lambda e, idx=i: delete_note_handler(idx)),
                    on_click=lambda e, idx=i: load_note(idx),
                    content_padding=4,
                )
            )

    def create_note_handler(e):
        note_error.value = ""
        title = note_title_input.value.strip()
        if not title:
            note_error.value = "Title cannot be empty."
            page.update()
            return
        result = notes_manager.create_note(title)
        if not result["success"]:
            note_error.value = result["message"]
            page.update()
            return
        note_title_input.value = ""
        notes_manager.set_current_note(result["index"])
        load_note(result["index"])
        refresh_notes_list()
        page.update()

    def delete_note_handler(idx):
        result = notes_manager.delete_note(idx)
        if not result["success"]:
            note_error.value = result["message"]
        else:
            note_editor.value = ""
            note_editor.visible = False
            note_actions_row.visible = False
            suggestions_label.visible = False
            note_info.value = ""
            predictions_row.controls.clear()
        refresh_notes_list()
        page.update()

    def load_note(idx):
        result = notes_manager.set_current_note(idx)
        if not result["success"]:
            note_error.value = result["message"]
            page.update()
            return

        note_result = notes_manager.get_note(idx)
        if not note_result["success"]:
            note_error.value = note_result["message"]
            page.update()
            return

        note = note_result["note"]
        note_editor.value = note["content"]
        note_editor.visible = True
        note_lang.value = note.get("lang", "cz")
        note_actions_row.visible = True
        suggestions_label.visible = True
        note_info.value = f"Loaded: {note['title']}"
        refresh_notes_list()
        page.update()

    def save_note_handler(e):
        note_error.value = ""
        current = notes_manager.get_current_note()
        if not current["success"]:
            note_error.value = "Select or create a note first."
            page.update()
            return

        # Update content
        result = notes_manager.update_note(notes_manager.current_note_index, note_editor.value)
        if not result["success"]:
            note_error.value = result["message"]
            page.update()
            return

        # Update language
        lang_result = notes_manager.set_note_language(notes_manager.current_note_index, note_lang.value)
        if not lang_result["success"]:
            note_error.value = lang_result["message"]
            page.update()
            return

        note_error.value = "Saved!"
        note_error.color = SUCCESS_COLOR
        page.update()

    def on_text_change(e):
        lang = note_lang.value or "cz"
        preds = notes_manager.get_predictions(note_editor.value, lang)
        predictions_row.controls.clear()
        for p in preds:
            predictions_row.controls.append(
                ft.Chip(label=ft.Text(p, size=12), on_click=lambda e, word=p: insert_word(word))
            )
        page.update()

    def insert_word(word):
        # Replace the current incomplete word
        text = note_editor.value
        words = text.split()
        if words:
            text = " ".join(words[:-1])
            if text:
                text += " "
        note_editor.value = text + word + " "
        predictions_row.controls.clear()
        page.update()

    note_editor.on_change = on_text_change

    note_actions_row = ft.Row([note_lang, btn("Save", save_note_handler, primary=True)], visible=False)

    refresh_notes_list()

    # Notepad: outer column doesn't scroll, inner elements handle their own overflow
    notes_page_content = ft.Column([
        section("Notepad"),
        sub("Create/load a note to start writing with word prediction."),
        ft.Row([note_title_input, btn("New Note", create_note_handler)]),
        note_error,
        note_info,
        ft.Row([
            # Left: notes list stuck to top, scrollable internally
            ft.Container(
                content=ft.Column([
                    notes_list_header,
                    ft.Container(content=notes_list, expand=True),
                ], spacing=4, scroll=ft.ScrollMode.AUTO),
                width=180,
                alignment=ft.Alignment(0, -1),
            ),
            ft.VerticalDivider(),
            # Right: fixed-height suggestions area at top, textbox fills remaining space
            ft.Column([
                ft.Container(
                    content=ft.Column([
                        suggestions_label,
                        predictions_row,
                    ], spacing=4),
                    height=60,  # Fixed height for suggestions area
                ),
                ft.Container(
                    content=note_editor,
                    expand=True,
                    # Add border to visually distinguish editor area
                    border=ft.Border.all(1, GREY_300_COLOR),
                    border_radius=4,
                ),
                note_actions_row,
            ], spacing=6, expand=True),
        ], expand=True),
    ], spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 6: Lunch Menu
    # ═══════════════════════════════════════════════════════
    lunch_manager = LunchMenuManager()
    lunch_error = ft.Text("", size=12, color=ERROR_COLOR)
    lunch_display = ft.Column(spacing=8)
    lunch_loading = ft.Text("Loading menu...", size=13, color=GREY_COLOR)
    lunch_status = ft.Text("", size=12, color=GREY_500_COLOR)

    def load_lunch(e=None):
        lunch_loading.visible = True
        lunch_error.value = ""
        lunch_status.value = ""
        lunch_display.controls.clear()
        page.update()

        result = lunch_manager.fetch_menu()

        lunch_loading.visible = False

        if not result["success"]:
            lunch_error.value = result["message"]
            page.update()
            return

        menu = result["menu"]
        lunch_status.value = f"Menu updated at {lunch_manager.last_fetch_time.strftime('%H:%M')}"

        if not menu:
            lunch_error.value = "No menu data found."
            page.update()
            return

        for day in menu:
            if not day["meals"]:
                continue
            day_label = day["day_name"] or day["date"] or "Unknown day"
            day_items = []
            for meal in day["meals"]:
                if meal["name"]:
                    day_items.append(ft.Text(meal["name"], size=13, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR))
                for i, item in enumerate(meal["items"]):
                    if i == 0:
                        icon = ft.Icons.SOUP_KITCHEN
                        color = ORANGE_COLOR
                    elif i == 1:
                        icon = ft.Icons.DINNER_DINING
                        color = BROWN_COLOR
                    else:
                        icon = ft.Icons.RICE_BOWL
                        color = GREEN_700_COLOR
                    day_items.append(
                        ft.Row([
                            ft.Icon(icon, size=12, color=color),
                            ft.Text(item, size=12),
                        ], spacing=6)
                    )
            if not day_items:
                day_items.append(ft.Text("No items listed", size=12, color=GREY_500_COLOR))

            lunch_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(day_label, size=14, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR),
                    ] + day_items, spacing=3),
                    padding=8,
                    border_radius=8,
                    bgcolor="#1F000000",
                )
            )

        page.update()

    # Load menu on startup
    load_lunch()

    lunch_page_content = ft.Column([
        section("Lunch Menu (Jídelníček)"),
        sub("Daily lunch options from stravovani.sspbrno.cz"),
        ft.Row([btn("Refresh", load_lunch)]),
        lunch_loading,
        lunch_status,
        lunch_error,
        lunch_display,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 7: EduPage Dashboard with Grade Calculator
    # ═══════════════════════════════════════════════════════
    edu_manager = EduPageManager()
    edu_subdomain = ft.TextField(label="School subdomain", width=180, content_padding=8)
    edu_user = ft.TextField(label="Username", width=180, content_padding=8)
    edu_pass = ft.TextField(label="Password", width=180, password=True, can_reveal_password=True, content_padding=8)
    edu_error = ft.Text("", size=12, color=ERROR_COLOR)
    edu_status = ft.Text("", size=13, color=SUCCESS_COLOR)
    edu_content = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    edu_remember = ft.Checkbox(label="Remember credentials", value=False)

    # Manual grade inputs
    manual_subject_input = ft.TextField(label="Subject", width=150, content_padding=8)
    manual_grade_input = ft.TextField(label="Grade (1-5)", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)
    manual_weight_input = ft.TextField(label="Weight", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)
    manual_grades_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    target_input = ft.TextField(label="Target avg (1=best)", width=120, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)
    target_result = ft.Text("", size=13)

    # Load saved credentials if any
    saved = edu_manager.load_saved_credentials()
    if saved:
        edu_subdomain.value = saved["subdomain"]
        edu_user.value = saved["username"]
        edu_pass.value = saved["password"]
        edu_remember.value = True

    def build_manual_grades():
        manual_grades_display.controls.clear()
        manual_grades = edu_manager.get_manual_grades()["grades"]
        for subject, grades_list in manual_grades.items():
            subject_container = ft.Column([
                ft.Text(subject, size=14, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR)
            ], spacing=2)
            for i, (g, w) in enumerate(grades_list):
                subject_container.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.STAR, size=14, color=AMBER_COLOR),
                        ft.Text(f"Grade: {g} × Weight: {w}", size=13),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_size=14,
                            tooltip="Remove",
                            on_click=lambda e, s=subject, idx=i: remove_manual_grade(s, idx),
                        ),
                    ], spacing=8)
                )
            manual_grades_display.controls.append(subject_container)

    def add_manual_grade(e):
        edu_error.value = ""
        subject = manual_subject_input.value.strip()
        if not subject:
            edu_error.value = "Subject cannot be empty."
            page.update()
            return
        try:
            grade = int(manual_grade_input.value)
        except (ValueError, TypeError):
            edu_error.value = "Grade must be a valid integer."
            page.update()
            return
        try:
            weight = float(manual_weight_input.value)
        except (ValueError, TypeError):
            edu_error.value = "Weight must be a valid number."
            page.update()
            return

        result = edu_manager.add_manual_grade(subject, grade, weight)
        if result["success"]:
            manual_subject_input.value = ""
            manual_grade_input.value = ""
            manual_weight_input.value = ""
            build_manual_grades()
            target_result.value = ""
        else:
            edu_error.value = result["message"]
        page.update()

    def remove_manual_grade(subject, index):
        result = edu_manager.remove_manual_grade(subject, index)
        if result["success"]:
            build_manual_grades()
            target_result.value = ""
        else:
            edu_error.value = result["message"]
        page.update()

    def calc_target(e):
        target_result.value = ""
        try:
            target = float(target_input.value)
        except (ValueError, TypeError):
            target_result.value = "Enter a valid target average."
            page.update()
            return

        # Get all grades (EduPage + manual) for calculation
        dashboard_data = edu_manager.get_dashboard_data()
        if not dashboard_data["success"]:
            target_result.value = "No grades available."
            page.update()
            return

        all_grades = []
        for subj in dashboard_data["grades"]["subjects"]:
            for g in subj["grades"]:
                try:
                    grade_val = float(g["grade"])
                    weight = float(g.get("weight", 1))
                    all_grades.append((grade_val, weight))
                except (ValueError, TypeError):
                    continue

        if not all_grades:
            target_result.value = "No valid grades found."
            page.update()
            return

        result = edu_manager.calculate_target_grade(all_grades, target)
        target_result.value = result["message"]
        page.update()

    def edu_login(e):
        edu_error.value = ""
        edu_status.value = ""
        edu_content.controls.clear()
        page.update()

        sub = edu_subdomain.value.strip()
        user = edu_user.value.strip()
        pw = edu_pass.value.strip()

        if not sub or not user or not pw:
            edu_error.value = "All fields are required."
            page.update()
            return

        edu_manager.set_credentials(sub, user, pw, edu_remember.value)

        login_result = edu_manager.login()
        if not login_result["success"]:
            edu_error.value = login_result["message"]
            page.update()
            return

        edu_status.value = "Logged in! Loading data..."
        page.update()

        # Get integrated dashboard data
        dashboard = edu_manager.get_dashboard_data()
        if not dashboard["success"]:
            edu_error.value = dashboard["message"]
            page.update()
            return

        edu_content.controls.clear()

        # Grades section with integrated averages
        edu_content.controls.append(section("Grades & Averages"))
        if dashboard["grades"]["success"]:
            overall_avg = dashboard["grades"]["overall_average"]
            if overall_avg > 0:
                edu_content.controls.append(
                    ft.Text(f"Overall weighted average: {overall_avg:.2f}",
                           size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
                )

            for subj in dashboard["grades"]["subjects"]:
                subj_items = []
                for g in subj["grades"]:
                    source_icon = ft.Icons.CLOUD if g.get("source") != "manual" else ft.Icons.EDIT
                    subj_items.append(
                        ft.Row([
                            ft.Icon(source_icon, size=12, color=BLUE_COLOR if g.get("source") != "manual" else ORANGE_COLOR),
                            ft.Text(f"{g['grade']} (w:{g.get('weight',1)}) - {g.get('date','')} {g.get('title','')}", size=12)
                        ], spacing=4)
                    )

                subj_col = ft.Column([
                    ft.Text(subj["name"], size=14, weight=ft.FontWeight.W_600),
                ] + subj_items, spacing=2)

                if "weighted_average" in subj and subj["weighted_average"] > 0:
                    subj_col.controls.append(
                        ft.Text(f"Average: {subj['weighted_average']:.2f}", size=13, weight=ft.FontWeight.W_500, color=SECONDARY_COLOR)
                    )

                edu_content.controls.append(subj_col)

            # Class comparison
            if dashboard["class_averages"]["success"]:
                edu_content.controls.append(ft.Divider())
                edu_content.controls.append(section("Class Comparison"))
                for subj_name, class_avg in dashboard["class_averages"]["averages"].items():
                    edu_content.controls.append(
                        ft.Text(f"{subj_name}: class avg {class_avg:.2f}", size=13)
                    )
        else:
            edu_content.controls.append(ft.Text(dashboard["grades"]["message"], size=13, color=GREY_500_COLOR))

        # Other sections (timetable, homework, etc.) - same as before but using dashboard data
        # Timetable
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Timetable"))
        if dashboard["timetable"]["success"]:
            for day in dashboard["timetable"]["days"]:
                edu_content.controls.append(ft.Text(day["date"], size=14, weight=ft.FontWeight.W_600))
                for lesson in day["lessons"]:
                    edu_content.controls.append(
                        ft.Text(f"  {lesson.get('hour','')}  {lesson.get('subject','')}  |  {lesson.get('teacher','')}  |  {lesson.get('room','')}", size=12)
                    )
        else:
            edu_content.controls.append(ft.Text(dashboard["timetable"]["message"], size=13, color=GREY_500_COLOR))

        # Homework
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Homework"))
        if dashboard["homework"]["success"]:
            for hw in dashboard["homework"]["assignments"]:
                status_icon = ft.Icons.CHECK_CIRCLE if hw["completed"] else ft.Icons.PENDING
                edu_content.controls.append(
                    ft.Row([
                        ft.Icon(status_icon, size=14, color=SUCCESS_COLOR if hw["completed"] else ORANGE_COLOR),
                        ft.Text(f"{hw['subject']}: {hw['title']} (due: {hw['due']})", size=13),
                    ], spacing=8)
                )
        else:
            edu_content.controls.append(ft.Text(dashboard["homework"]["message"], size=13, color=GREY_500_COLOR))

        # Tests
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Upcoming Tests"))
        if dashboard["tests"]["success"]:
            for t in dashboard["tests"]["tests"]:
                edu_content.controls.append(
                    ft.Text(f"{t['subject']}: {t['title']} on {t['date']} ({t.get('type','')})", size=13)
                )
        else:
            edu_content.controls.append(ft.Text(dashboard["tests"]["message"], size=13, color=GREY_500_COLOR))

        # Substitutions
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Substitutions"))
        if dashboard["substitutions"]["success"]:
            for s_item in dashboard["substitutions"]["substitutions"]:
                edu_content.controls.append(
                    ft.Text(f"{s_item['date']} Hr.{s_item['hour']}: {s_item['title']} [{s_item['action']}] {s_item['class']}", size=12)
                )
        else:
            edu_content.controls.append(ft.Text(dashboard["substitutions"]["message"], size=13, color=GREY_500_COLOR))

        edu_status.value = "Data loaded."
        page.update()

    # Build initial manual grades display
    build_manual_grades()

    edu_page_content = ft.Column([
        section("EduPage Dashboard & Grade Calculator"),
        sub("Login to sync EduPage data and manage manual grades for weighted average calculation."),
        ft.Row([edu_subdomain, edu_user, edu_pass, btn("Login", edu_login, primary=False)]),
        edu_remember,
        edu_error,
        edu_status,

        ft.Divider(),
        section("Manual Grades"),
        sub("Add grades for subjects not in EduPage or additional entries."),
        ft.Row([manual_subject_input, manual_grade_input, manual_weight_input, btn("Add Grade", add_manual_grade)]),
        ft.Container(content=manual_grades_display, height=150),

        ft.Divider(),
        section("Target Calculator"),
        sub("Find what grade you need to reach a target average."),
        ft.Row([target_input, btn("Calculate Target", calc_target)]),
        target_result,

        ft.Divider(),
        section("Dashboard Data"),
        edu_content,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 8: Scientific Calculator
    # ═══════════════════════════════════════════════════════
    sci_calc = ScientificCalculator.ScientificCalculator()
    sci_input = ft.TextField(label="Expression", width=300, content_padding=8)
    sci_result = ft.Text("", size=16, weight=ft.FontWeight.W_500)
    sci_error = ft.Text("", size=12, color=ERROR_COLOR)
    sci_functions_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    sci_examples_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    sci_history_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    def sci_evaluate(e):
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
        sci_functions_display.controls.clear()
        functions_result = sci_calc.get_available_functions()
        if functions_result["success"]:
            functions = functions_result["functions"]
            # Group functions
            math_funcs = [f for f in functions if not f.startswith('_')]
            sci_functions_display.controls.append(
                ft.Text("Available functions:", size=13, weight=ft.FontWeight.W_600)
            )
            sci_functions_display.controls.append(
                ft.Text(", ".join(math_funcs), size=12, selectable=True)
            )
        page.update()

    def update_sci_examples():
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
        sci_history_display.controls.clear()
        history_result = sci_calc.get_history()
        if history_result["success"] and history_result["history"]:
            sci_history_display.controls.append(
                ft.Text("Recent calculations:", size=13, weight=ft.FontWeight.W_600)
            )
            for item in history_result["history"]:
                sci_history_display.controls.append(
                    ft.Text(f"{item['expression']} = {item['result']}", size=12)
                )
        page.update()

    def sci_clear_history(e):
        result = sci_calc.clear_history()
        if result["success"]:
            update_sci_history()
        page.update()

    # Initialize displays
    update_sci_functions()
    update_sci_examples()
    update_sci_history()

    sci_page_content = ft.Column([
        section("Scientific Calculator"),
        sub("Evaluate mathematical expressions with trigonometric, exponential, and other functions."),
        ft.Row([sci_input, btn("Calculate", sci_evaluate, primary=True)]),
        sci_error,
        sci_result,
        ft.Divider(),
        ft.Row([
            ft.Column([
                section("Functions"),
                ft.Container(content=sci_functions_display, height=150),
            ], expand=1),
            ft.VerticalDivider(),
            ft.Column([
                section("Examples"),
                ft.Container(content=sci_examples_display, height=150),
            ], expand=1),
            ft.VerticalDivider(),
            ft.Column([
                section("History"),
                ft.Container(content=sci_history_display, height=150),
                btn("Clear History", sci_clear_history),
            ], expand=1),
        ], expand=True),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 9: Wolfram Alpha
    # ═══════════════════════════════════════════════════════
    wolf_manager = WolframAlphaManager()
    wolf_status_row = ft.Row([ft.Icon(ft.Icons.CLOUD_OFF, size=20, color=ERROR_COLOR)], spacing=0)
    wolf_status_text = ft.Text("Not logged in", size=12, color=ERROR_COLOR)
    wolf_error = ft.Text("", size=12, color=ERROR_COLOR)
    wolf_api_input = ft.TextField(label="API Key", width=250, password=True, can_reveal_password=True, content_padding=8)
    wolf_query_input = ft.TextField(label="Ask Wolfram Alpha...", width=400, content_padding=8)
    wolf_assumptions_input = ft.TextField(label="Assumptions (comma-separated, optional)", width=300, content_padding=8, visible=False)
    wolf_result_display = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    wolf_history_list = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
    wolf_view_mode = ["simple"]  # "simple" or "detailed"
    wolf_current_result = {"simple": [], "detailed": []}

    def wolf_update_status():
        """Update login status display."""
        if wolf_manager.has_api_key():
            wolf_status_row.controls[0] = ft.Icon(ft.Icons.CLOUD_DONE, size=20, color=SUCCESS_COLOR)
            wolf_status_text.value = "Logged in"
            wolf_status_text.color = SUCCESS_COLOR
        else:
            wolf_status_row.controls[0] = ft.Icon(ft.Icons.CLOUD_OFF, size=20, color=ERROR_COLOR)
            wolf_status_text.value = "Not logged in"
            wolf_status_text.color = ERROR_COLOR
        page.update()

    def wolf_open_portal(e):
        """Open API portal in browser."""
        wolf_error.value = ""
        if wolf_manager.open_portal():
            wolf_error.value = "Opened API portal in browser. Copy your API key and paste it below."
            wolf_error.color = BLUE_COLOR
        else:
            wolf_error.value = "Could not open browser. Visit https://products.wolframalpha.com/api/"
            wolf_error.color = ORANGE_COLOR
        page.update()

    def wolf_paste_key(e):
        """Paste API key from clipboard and validate."""
        wolf_error.value = ""
        try:
            import pyperclip
            clipboard_text = pyperclip.paste().strip()
        except Exception:
            wolf_error.value = "Could not access clipboard. Please paste manually."
            page.update()
            return

        if not clipboard_text:
            wolf_error.value = "Clipboard is empty."
            page.update()
            return

        wolf_api_input.value = clipboard_text

        # Validate and set key
        result = wolf_manager.set_api_key(clipboard_text)
        wolf_error.value = result["message"]
        wolf_error.color = SUCCESS_COLOR if result["success"] else ERROR_COLOR
        wolf_update_status()
        page.update()

    def wolf_forget_key(e):
        """Clear saved API key."""
        result = wolf_manager.clear_api_key()
        wolf_api_input.value = ""
        wolf_error.value = result["message"]
        wolf_error.color = ORANGE_COLOR
        wolf_update_status()
        page.update()

    def wolf_validate_manual_key(e):
        """Validate manually entered API key."""
        wolf_error.value = ""
        input_text = wolf_api_input.value.strip()

        if not input_text:
            wolf_error.value = "Please enter an API key."
            wolf_error.color = ORANGE_COLOR
            page.update()
            return

        # Validate and set key
        result = wolf_manager.set_api_key(input_text)
        wolf_error.value = result["message"]
        wolf_error.color = SUCCESS_COLOR if result["success"] else ERROR_COLOR
        wolf_update_status()
        page.update()

    def wolf_execute_query(e):
        """Execute Wolfram Alpha query."""
        wolf_error.value = ""
        wolf_result_display.controls.clear()
        page.update()

        if not wolf_query_input.value.strip():
            wolf_error.value = "Enter a query."
            page.update()
            return

        if not wolf_manager.has_api_key():
            wolf_error.value = "Please log in first."
            page.update()
            return

        # Parse assumptions
        assumptions = []
        if wolf_assumptions_input.value.strip():
            assumptions = [a.strip() for a in wolf_assumptions_input.value.split(",")]

        # Query
        result = wolf_manager.query(wolf_query_input.value, assumptions)

        if not result["success"]:
            wolf_error.value = result["message"]
            wolf_error.color = ERROR_COLOR
            page.update()
            return

        wolf_current_result = result["results"]
        wolf_error.value = result["message"]
        wolf_error.color = SUCCESS_COLOR

        # Display results
        wolf_display_results()

        # Refresh history
        wolf_refresh_history()

        page.update()

    def wolf_display_results():
        """Display current results based on view mode."""
        wolf_result_display.controls.clear()

        if wolf_view_mode[0] == "simple":
            results = wolf_current_result.get("simple", [])
            for i, res_text in enumerate(results):
                wolf_result_display.controls.append(
                    ft.Container(
                        content=ft.Text(res_text, size=13, selectable=True),
                        padding=10,
                        border_radius=6,
                        bgcolor="#1F000000",
                        border=ft.Border.all(1, GREY_400_COLOR)
                    )
                )
        else:  # detailed
            detailed = wolf_current_result.get("detailed", [])
            for pod in detailed:
                pod_content = [
                    ft.Text(pod["title"], size=13, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR)
                ]
                for subpod in pod.get("subpods", []):
                    pod_content.append(
                        ft.Text(subpod.get("text", ""), size=12, selectable=True)
                    )

                wolf_result_display.controls.append(
                    ft.Container(
                        content=ft.Column(pod_content, spacing=4),
                        padding=10,
                        border_radius=6,
                        bgcolor="#1F000000",
                        border=ft.Border.all(1, BLUE_300_COLOR)
                    )
                )

    def wolf_toggle_view(e):
        """Toggle between simple and detailed view."""
        wolf_view_mode[0] = "detailed" if wolf_view_mode[0] == "simple" else "simple"
        view_btn.text = "📊 Detailed" if wolf_view_mode[0] == "simple" else "📝 Simple"
        wolf_display_results()
        page.update()

    def wolf_load_history(idx):
        """Load query from history."""
        history = wolf_manager.get_history()
        if idx < len(history):
            item = history[idx]
            wolf_current_result = item.get("results", {"simple": [], "detailed": []})
            wolf_display_results()
            page.update()

    def wolf_refresh_history():
        """Rebuild history sidebar."""
        history = wolf_manager.get_history()
        wolf_history_list.controls.clear()

        for i, item in enumerate(history):
            query_text = item.get("query", "")[:50] + ("..." if len(item.get("query", "")) > 50 else "")
            wolf_history_list.controls.append(
                ft.Column([
                    ft.ListTile(
                        title=ft.Text(query_text, size=12),
                        trailing=ft.Icon(ft.Icons.HISTORY, size=14),
                        on_click=lambda e, idx=i: wolf_load_history(idx),
                        content_padding=4,
                    ),
                    ft.Divider(height=1),
                ], spacing=0)
            )

    def wolf_clear_history(e):
        """Clear query history."""
        result = wolf_manager.clear_history()
        wolf_refresh_history()
        wolf_error.value = result["message"]
        wolf_error.color = ORANGE_COLOR
        page.update()

    view_btn = btn("📊 Detailed", wolf_toggle_view)
    wolf_update_status()
    wolf_refresh_history()

    wolf_page_content = ft.Column([
        section("Wolfram Alpha Query"),

        # Login section
        ft.Row([
            ft.Icon(ft.Icons.LOCK_OPEN, size=20, color=BLUE_COLOR),
            ft.Column([
                ft.Text("Log in to Wolfram Alpha", size=13, weight=ft.FontWeight.W_600),
                ft.Text("Click 'Open Portal' → log in → click 'Get an App ID' → fill out and select 'Full Results API' → copy App ID → click 'Paste'", size=11, color=GREY_COLOR),
            ], spacing=2, expand=True),
        ], spacing=12, alignment=ft.MainAxisAlignment.START),

        ft.Row([
            btn("🌐 Open Portal", wolf_open_portal),
            btn("📋 Paste Key", wolf_paste_key),
            btn("✓ Validate", wolf_validate_manual_key),
            btn("🗑️ Forget", wolf_forget_key),
            ft.Row([wolf_status_row, wolf_status_text], spacing=6),
        ], spacing=8),

        wolf_api_input,
        wolf_error,

        ft.Divider(),

        # Query section
        section("Query"),
        ft.Row([
            wolf_query_input,
            btn("🔍 Evaluate", wolf_execute_query, primary=True),
            view_btn,
        ], spacing=8),

        ft.Row([wolf_assumptions_input], spacing=8),

        # Results + History
        ft.Row([
            # Results (left, main)
            ft.Container(
                content=wolf_result_display,
                expand=True,
                border_radius=6,
                border=ft.Border.all(1, GREY_400_COLOR),
                padding=10,
            ),

            # History sidebar (right)
            ft.Column([
                ft.Text("History", size=12, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=wolf_history_list,
                    width=150,
                    height=300,
                    border_radius=6,
                    border=ft.Border.all(1, GREY_300_COLOR),
                    padding=4,
                ),
                btn("Clear", wolf_clear_history),
            ], spacing=6),
        ], spacing=12, expand=True),

    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # Navigation
    # ═══════════════════════════════════════════════════════
    tab_bar_view = ft.TabBarView(controls=[
        subnet_page_content,
        base_page_content,
        bool_page_content,
        unit_page_content,
        fc_page_content,
        notes_page_content,
        lunch_page_content,
        edu_page_content,
        sci_page_content,
        wolf_page_content,
    ])

    nav = ft.Tabs(
        length=10,
        selected_index=0,
        expand=True,
        content=ft.Column([
            ft.TabBar(tabs=[
                ft.Tab(label="Subnets"),
                ft.Tab(label="Base Calc"),
                ft.Tab(label="Bool Alg"),
                ft.Tab(label="Units"),
                ft.Tab(label="Flashcards"),
                ft.Tab(label="Notepad"),
                ft.Tab(label="Lunch"),
                ft.Tab(label="EduPage"),
                ft.Tab(label="Sci Calc"),
                ft.Tab(label="Wolfram"),
            ]),
            ft.Container(content=tab_bar_view, expand=True),
        ], spacing=0, expand=True),
    )

    page.add(header, nav)

ft.run(main)