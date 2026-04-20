import flet as ft
from Calculator import calculate_weighted_average
from IPv4Subnetting import calculate_subnets
from MultiBaseConverter import convert
from MultiBaseCalc import evaluate as eval_multi_base
from UnitConverter import get_categories, get_units, convert_all
from BooleanAlgebra import simplify_expression
#from ScientificCalculator import evaluate_expression, get_available_functions, get_examples
import Flashcards
import Notes
from EduPage import EduSession
from EduPage import save_credentials, load_credentials, clear_credentials
from Lunch import fetch_lunch_menu
import WolframAlpha


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
            ft.Text("IT Toolbox", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
            theme_icon,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    def btn(label, on_click, primary=False):
        return ft.Button(
            content=ft.Text(label, size=12),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY if primary else ft.Colors.SURFACE,
                color=ft.Colors.ON_PRIMARY if primary else ft.Colors.ON_SURFACE,
                side=ft.BorderSide(width=1, color=ft.Colors.PRIMARY) if not primary else None,
            ),
            on_click=on_click,
        )

    def section(text):
        return ft.Text(text, size=18, weight=ft.FontWeight.W_600)

    def sub(text):
        return ft.Text(text, size=12, color=ft.Colors.GREY_600)

    # ═══════════════════════════════════════════════════════
    # TAB 0: Weighted Grade Calculator
    # ═══════════════════════════════════════════════════════
    grades_list: list[tuple[int, float]] = []
    grade_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    grade_error = ft.Text("", size=12, color=ft.Colors.RED)
    grade_result = ft.Text("", size=16, weight=ft.FontWeight.W_500)
    grade_input = ft.TextField(label="Grade (1-5)", width=110, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)
    weight_input = ft.TextField(label="Weight", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)
    target_input = ft.TextField(label="Target avg (1=best)", width=120, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)
    target_result = ft.Text("", size=13)

    def build_grades():
        grade_display.controls.clear()
        for i, (g, w) in enumerate(grades_list):
            grade_display.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.STAR, size=14, color=ft.Colors.AMBER),
                    ft.Text(f"Grade: {g}  ×  Weight: {w}", size=13),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_size=14,
                        tooltip="Remove",
                        on_click=lambda e, idx=i: (grades_list.pop(idx), build_grades(), page.update()),
                    ),
                ], spacing=8)
            )

    def add_grade(e):
        grade_error.value = ""
        try:
            grade = int(grade_input.value)
        except (ValueError, TypeError):
            grade_error.value = "Grade must be a valid integer."
            page.update()
            return
        if grade < 1 or grade > 5:
            grade_error.value = "Grade must be between 1 and 5."
            page.update()
            return
        try:
            weight = float(weight_input.value)
        except (ValueError, TypeError):
            grade_error.value = "Weight must be a valid number."
            page.update()
            return
        if weight <= 0:
            grade_error.value = "Weight must be greater than 0."
            page.update()
            return
        grades_list.append((grade, weight))
        grade_input.value = ""
        weight_input.value = ""
        build_grades()
        grade_result.value = ""
        target_result.value = ""
        page.update()

    def calc_grade(e):
        result = calculate_weighted_average(grades_list)
        grade_result.value = result["message"]
        page.update()

    def calc_target(e):
        target_result.value = ""
        try:
            target = float(target_input.value)
        except (ValueError, TypeError):
            target_result.value = "Enter a valid target average."
            page.update()
            return
        if target < 1 or target > 5:
            target_result.value = "Target must be between 1 and 5."
            page.update()
            return
        if not grades_list:
            target_result.value = "Enter at least one grade first."
            page.update()
            return

        current_sum = sum(g * w for g, w in grades_list)
        current_weight = sum(w for _, w in grades_list)
        current_avg = current_sum / current_weight

        if current_avg <= target:
            target_result.value = (
                f"Current average {current_avg:.2f} is already ≤ {target}. "
                "No improvement needed (1 is the best in Czech grading!)"
            )
            page.update()
            return

        # Find combinations of grades (1-5) with weights [0.2, 0.5, 1, 2, 3] to reach/surpass target
        weights = [0.2, 0.5, 1, 2, 3]
        grades = [1, 2, 3, 4, 5]
        
        lines = [f"Current average: {current_avg:.2f}. Target: {target}. Options to reach/surpass target:"]
        
        # Check single additional grade/weight combinations
        single_options = []
        for w in weights:
            for g in grades:
                new_sum = current_sum + (g * w)
                new_weight = current_weight + w
                new_avg = new_sum / new_weight
                if new_avg <= target:  # Remember: lower is better in Czech grading
                    single_options.append((g, w, new_avg))
        
        if single_options:
            # Sort by how close to target (without going over), then by weight (prefer smaller weights)
            single_options.sort(key=lambda x: (target - x[2], x[1]))
            lines.append("  Single additional grade/weight options:")
            for g, w, avg in single_options[:5]:  # Show top 5 options
                lines.append(f"    Grade {g} with weight {w} → new average: {avg:.2f}")
        else:
            lines.append("  No single grade/weight combination can reach the target.")
        
        # Check combinations of two grades/weights (limited search for performance)
        two_options = []
        for w1 in weights:
            for g1 in grades:
                for w2 in weights:
                    for g2 in grades:
                        new_sum = current_sum + (g1 * w1) + (g2 * w2)
                        new_weight = current_weight + w1 + w2
                        new_avg = new_sum / new_weight
                        if new_avg <= target:
                            two_options.append(((g1, w1), (g2, w2), new_avg))
        
        if two_options:
            # Sort by how close to target, then by total weight
            two_options.sort(key=lambda x: (target - x[2], x[0][1] + x[1][1]))
            lines.append("  Two grade/weight combinations (showing best 5):")
            for (g1, w1), (g2, w2), avg in two_options[:5]:
                lines.append(f"    Grade {g1} (weight {w1}) + Grade {g2} (weight {w2}) → new average: {avg:.2f}")
        else:
            lines.append("  No two grade/weight combinations can reach the target.")
        
        # If still no options, suggest needing multiple good grades
        if not single_options and not two_options:
            lines.append("  Need multiple good grades (better than current average) to reach target.")
            lines.append(f"  Current average: {current_avg:.2f}, Target: {target}")
            lines.append("  Try adding several grades of 1 or 2 with various weights.")

        target_result.value = "\n".join(lines)
        page.update()

    def reset_grade(e):
        grades_list.clear()
        build_grades()
        grade_result.value = ""
        grade_error.value = ""
        target_result.value = ""
        page.update()

    grade_page_content = ft.Column([
        section("Weighted Grade Calculator"),
        sub("Add grades, remove individually with the delete icon."),
        ft.Row([grade_input, weight_input, btn("Add", add_grade)]),
        grade_error,
        ft.Container(content=grade_display, expand=True),
        ft.Row([btn("Calculate", calc_grade, primary=True), btn("Reset", reset_grade)]),
        grade_result,
        ft.Divider(),
        section("Target Average"),
        sub("Find what grade you need to reach a target (lower is better)."),
        ft.Row([target_input, btn("Calculate", calc_target)]),
        target_result,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 1: IPv4 Subnet Calculator
    # ═══════════════════════════════════════════════════════
    segments_list: list[int] = []
    subnet_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    subnet_error = ft.Text("", size=12, color=ft.Colors.RED)
    subnet_result_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    network_input = ft.TextField(label="Network (e.g. 192.168.10.0/24)", width=280, content_padding=8)
    segment_input = ft.TextField(label="Users", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)

    def build_segments():
        subnet_display.controls.clear()
        for i, u in enumerate(segments_list):
            subnet_display.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.ROUTER, size=14, color=ft.Colors.BLUE),
                    ft.Text(f"Segment {i+1}: {u} users", size=13),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=14,
                        on_click=lambda e, idx=i: (segments_list.pop(idx), build_segments(), page.update()),
                    ),
                ], spacing=8)
            )

    def add_segment(e):
        subnet_error.value = ""
        try:
            users = int(segment_input.value)
        except (ValueError, TypeError):
            subnet_error.value = "Enter a valid number."
            page.update()
            return
        if users <= 0 or users > 65534:
            subnet_error.value = "Users must be between 1 and 65534."
            page.update()
            return
        segments_list.append(users)
        segment_input.value = ""
        build_segments()
        subnet_result_col.controls.clear()
        page.update()

    def calc_subnet(e):
        subnet_result_col.controls.clear()
        result = calculate_subnets(network_input.value, segments_list)
        if not result["success"]:
            subnet_result_col.controls.append(ft.Text(result["message"], size=13, color=ft.Colors.RED))
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
        segments_list.clear()
        build_segments()
        subnet_result_col.controls.clear()
        network_input.value = ""
        segment_input.value = ""
        subnet_error.value = ""
        page.update()

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
    # TAB 2: Multi-Base Calculator
    # ═══════════════════════════════════════════════════════
    base_error = ft.Text("", size=12, color=ft.Colors.RED)
    base_results = ft.Column(spacing=6)
    base_value_input = ft.TextField(label="Value", width=160, content_padding=8)
    base_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("2"), ft.dropdown.Option("8"), ft.dropdown.Option("10"), ft.dropdown.Option("16")],
        value="10", width=100, label="From Base", content_padding=8,
    )
    expr_input = ft.TextField(label="Equation (e.g. 0b1010 + 0xFF)", width=300, content_padding=8)
    expr_results = ft.Column(spacing=6)

    def convert_base(e):
        base_results.controls.clear()
        base_error.value = ""
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
        result = eval_multi_base(expr_input.value)
        if not result["success"]:
            base_error.value = result["message"]
            page.update()
            return
        expr_results.controls.append(ft.Text(f"Result: {result['results']['Decimal']}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY))
        for name, val in result["results"].items():
            prefix = {"Binary": "0b", "Octal": "0o", "Hexadecimal": "0x"}.get(name, "")
            expr_results.controls.append(
                ft.Row([ft.Text(f"{name}:", width=100, weight=ft.FontWeight.W_600), ft.Text(f"{prefix}{val}", size=14)], spacing=8)
            )
        page.update()

    def reset_base(e):
        base_value_input.value = ""
        base_results.controls.clear()
        expr_input.value = ""
        expr_results.controls.clear()
        base_error.value = ""
        page.update()

    base_page_content = ft.Column([
        section("Multi-Base Calculator"),
        ft.Row([base_value_input, base_dropdown, btn("Convert", convert_base)]),
        base_results,
        ft.Divider(),
        sub("Equation evaluator with mixed-base numbers (0b, 0o, 0x prefixes)."),
        ft.Row([expr_input, btn("Evaluate", eval_base_expr, primary=True)]),
        expr_results,
        ft.Divider(),
        btn("Reset", reset_base),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 3: Boolean Algebra Simplifier
    # ═══════════════════════════════════════════════════════
    bool_error = ft.Text("", size=12, color=ft.Colors.RED)
    bool_result = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    bool_input = ft.TextField(label="Expression (e.g. A·B + ~C)", width=300, content_padding=8)

    def simplify_bool(e):
        bool_result.controls.clear()
        bool_error.value = ""
        expr = bool_input.value.strip()
        if not expr:
            bool_error.value = "Enter a boolean expression."
            page.update()
            return
        result = simplify_expression(expr)
        if not result["success"]:
            bool_error.value = result["message"]
            page.update()
            return
        if result["type"] == "tautology":
            bool_result.controls.append(ft.Text(result["message"], size=14, color=ft.Colors.GREEN))
            page.update()
            return
        if result["type"] == "contradiction":
            bool_result.controls.append(ft.Text(result["message"], size=14, color=ft.Colors.RED))
            page.update()
            return

        bool_result.controls.append(ft.Text(f"Variables: {', '.join(result['vars'])}", size=13, weight=ft.FontWeight.W_600))
        bool_result.controls.append(ft.Text(f"SOP: {result['sop']}", size=13, selectable=True))
        bool_result.controls.append(ft.Text(f"POS: {result['pos']}", size=13, selectable=True))
        bool_result.controls.append(ft.Divider())
        bool_result.controls.append(ft.Text("Truth Table:", size=13, weight=ft.FontWeight.W_600))
        for assignment, res in result["table"]:
            vals = "  ".join(f"{v}={assignment[v]}" for v in result["vars"])
            bool_result.controls.append(
                ft.Row([ft.Text(vals, size=12), ft.Text(f" → {res}", size=12, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN if res else ft.Colors.RED)], spacing=8)
            )
        page.update()

    def reset_bool(e):
        bool_input.value = ""
        bool_result.controls.clear()
        bool_error.value = ""
        page.update()

    bool_page_content = ft.Column([
        section("Boolean Algebra Simplifier"),
        sub("Operators: + (OR), · (AND), ~ (NOT)"),
        ft.Row([bool_input, btn("Analyze", simplify_bool, primary=True), btn("Reset", reset_bool)]),
        bool_error,
        ft.Container(content=bool_result, expand=True),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 4: Unit Converter
    # ═══════════════════════════════════════════════════════
    def on_category_change(e):
        val = e.data if e and e.data else unit_current_category[0]
        unit_current_category[0] = val
        units = get_units(val) if val else []
        unit_from.options.clear()
        for u in units:
            unit_from.options.append(ft.dropdown.Option(u))
        if units:
            unit_from.value = units[0]
        else:
            unit_from.value = None
        unit_results.controls.clear()
        unit_value.value = ""
        page.update()
        
    unit_error = ft.Text("", size=12, color=ft.Colors.RED)
    unit_results = ft.Column(spacing=4)
    unit_current_category = [get_categories()[0]]  # mutable container

    unit_categories_dd = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in get_categories()],
        value=get_categories()[0], width=160, label="Category", content_padding=8,
        on_select=on_category_change
    )
    unit_from = ft.Dropdown(label="From", width=140, content_padding=8, data=unit_current_category)
    unit_value = ft.TextField(label="Value", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)


    def refresh_units(e):
        on_category_change(None)

    def convert_unit(e):
        unit_results.controls.clear()
        unit_error.value = ""
        try:
            val = float(unit_value.value)
        except (ValueError, TypeError):
            unit_error.value = "Enter a valid number."
            page.update()
            return
        result = convert_all(val, unit_current_category[0], unit_from.value)
        if not result["success"]:
            unit_error.value = result["message"]
            page.update()
            return
        for name, v in result["results"].items():
            color = ft.Colors.PRIMARY if name == unit_from.value else ft.Colors.ON_SURFACE
            weight = ft.FontWeight.W_600 if name == unit_from.value else ft.FontWeight.W_400
            unit_results.controls.append(
                ft.Row([ft.Text(f"{name}:", width=90, weight=weight, color=color), ft.Text(f"{v:.6g}", size=13)], spacing=8)
            )
        page.update()

    def reset_unit(e):
        unit_value.value = ""
        unit_results.controls.clear()
        unit_error.value = ""
        page.update()

    for u in get_units(get_categories()[0]):
        unit_from.options.append(ft.dropdown.Option(u))
    unit_from.value = get_units(get_categories()[0])[0]

    unit_page_content = ft.Column([
        section("Unit Converter"),
        ft.Row([unit_categories_dd, unit_from, unit_value, btn("Convert", convert_unit, primary=True), btn("Reset", reset_unit)]),
        unit_error,
        unit_results,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 5: Flashcards
    # ═══════════════════════════════════════════════════════
    decks = Flashcards.load_decks()
    fc_deck_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    fc_deck_selector = ft.Dropdown(label="Select Deck", width=200, content_padding=8)
    fc_new_deck_name = ft.TextField(label="New Deck Name", width=180, content_padding=8)
    fc_card_front = ft.TextField(label="Front", width=180, content_padding=8)
    fc_card_back = ft.TextField(label="Back", width=180, content_padding=8)
    fc_deck_error = ft.Text("", size=12, color=ft.Colors.RED)
    fc_card_display = ft.Column(spacing=8)

    def refresh_deck_list():
        fc_deck_list.controls.clear()
        fc_deck_selector.options.clear()
        for name in decks:
            count = len(decks[name])
            fc_deck_list.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.LAYERS, size=14, color=ft.Colors.TEAL),
                    ft.Text(f"{name} ({count})", size=13),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_size=14, on_click=lambda e, n=name: delete_deck_handler(n)),
                ], spacing=8)
            )
            fc_deck_selector.options.append(ft.dropdown.Option(name))
        if decks:
            fc_deck_selector.value = list(decks.keys())[0]

    def create_deck_handler(e):
        fc_deck_error.value = ""
        name = fc_new_deck_name.value.strip()
        if not name:
            fc_deck_error.value = "Deck name cannot be empty."
            page.update()
            return
        if Flashcards.create_deck(decks, name) is None:
            fc_deck_error.value = "Deck already exists."
            page.update()
            return
        fc_new_deck_name.value = ""
        refresh_deck_list()
        page.update()

    def delete_deck_handler(name):
        Flashcards.delete_deck(decks, name)
        Flashcards.save_decks(decks)
        refresh_deck_list()
        fc_card_display.controls.clear()
        page.update()

    def add_card_handler(e):
        fc_deck_error.value = ""
        deck_name = fc_deck_selector.value
        if not deck_name or deck_name not in decks:
            fc_deck_error.value = "Select or create a deck first."
            page.update()
            return
        front = fc_card_front.value.strip()
        back = fc_card_back.value.strip()
        if not front or not back:
            fc_deck_error.value = "Both front and back are required."
            page.update()
            return
        Flashcards.add_card(decks, deck_name, front, back)
        Flashcards.save_decks(decks)
        fc_card_front.value = ""
        fc_card_back.value = ""
        refresh_deck_list()
        page.update()

    def start_quiz_handler(e):
        fc_card_display.controls.clear()
        fc_deck_error.value = ""
        deck_name = fc_deck_selector.value
        if not deck_name or deck_name not in decks:
            fc_deck_error.value = "Select a deck first."
            page.update()
            return
        cards = Flashcards.start_quiz(decks, deck_name)
        if not cards:
            fc_deck_error.value = "Deck is empty."
            page.update()
            return

        def show_card(idx=0):
            fc_card_display.controls.clear()
            if idx >= len(cards):
                fc_card_display.controls.append(ft.Text("Quiz complete!", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN))
                page.update()
                return
            card = cards[idx]
            fc_card_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Front", size=11, color=ft.Colors.GREY_600),
                        ft.Text(card["front"], size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Back", size=11, color=ft.Colors.GREY_600),
                        ft.Text(card["back"], size=16),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20, border_radius=10, bgcolor="#1F000000", alignment=ft.alignment.center,
                )
            )
            fc_card_display.controls.append(
                ft.Row([btn(f"Next ({idx+1}/{len(cards)})", lambda e, i=idx+1: show_card(i), primary=True)],
                       alignment=ft.MainAxisAlignment.CENTER)
            )
            page.update()

        show_card()

    refresh_deck_list()

    fc_page_content = ft.Column([
        section("Flashcards"),
        ft.Row([fc_new_deck_name, btn("Create", create_deck_handler)]),
        ft.Row([fc_card_front, fc_card_back, btn("Add", add_card_handler)]),
        fc_deck_error,
        ft.Row([fc_deck_selector, btn("Quiz", start_quiz_handler, primary=True)]),
        ft.Container(content=fc_deck_list, expand=True),
        fc_card_display,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 6: Notepad with CZ/EN prediction
    # ═══════════════════════════════════════════════════════
    notes = Notes.load_notes()
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
    suggestions_label = ft.Text("Suggestions:", size=11, color=ft.Colors.GREY_500, visible=False)
    note_error = ft.Text("", size=12, color=ft.Colors.RED)
    note_info = ft.Text("", size=12, color=ft.Colors.GREY_500)
    note_actions_row = None  # created below after all handlers defined
    note_editor.visible = False
    current_note_idx: int = -1

    def refresh_notes_list():
        notes_list.controls.clear()
        notes_list_header.visible = len(notes) > 0
        for i, n in enumerate(notes):
            color = ft.Colors.PRIMARY if i == current_note_idx else ft.Colors.ON_SURFACE
            weight = ft.FontWeight.W_600 if i == current_note_idx else ft.FontWeight.W_400
            notes_list.controls.append(
                ft.ListTile(
                    title=ft.Text(n["title"], size=13, color=color, weight=weight),
                    trailing=ft.IconButton(icon=ft.Icons.DELETE_OUTLINED, icon_size=16, on_click=lambda e, idx=i: delete_note_handler(idx)),
                    on_click=lambda e, idx=i: load_note(idx),
                    content_padding=4,
                )
            )

    def create_note_handler(e):
        nonlocal current_note_idx
        note_error.value = ""
        title = note_title_input.value.strip()
        if not title:
            note_error.value = "Title cannot be empty."
            page.update()
            return
        Notes.create_note(notes, title)
        Notes.save_notes(notes)
        note_title_input.value = ""
        current_note_idx = len(notes) - 1
        load_note(current_note_idx)
        refresh_notes_list()
        page.update()

    def delete_note_handler(idx):
        nonlocal current_note_idx
        Notes.delete_note(notes, idx)
        Notes.save_notes(notes)
        current_note_idx = -1
        note_editor.value = ""
        note_editor.visible = False
        note_actions_row.visible = False
        suggestions_label.visible = False
        note_info.value = ""
        predictions_row.controls.clear()
        refresh_notes_list()
        page.update()

    def load_note(idx):
        nonlocal current_note_idx
        current_note_idx = idx
        note_editor.value = notes[idx]["content"]
        note_editor.visible = True
        note_lang.value = notes[idx].get("lang", "cz")
        note_actions_row.visible = True
        suggestions_label.visible = True
        note_info.value = f"Loaded: {notes[idx]['title']}"
        refresh_notes_list()
        page.update()

    def save_note_handler(e):
        note_error.value = ""
        if current_note_idx < 0 or current_note_idx >= len(notes):
            note_error.value = "Select or create a note first."
            page.update()
            return
        Notes.update_note(notes, current_note_idx, note_editor.value)
        Notes.set_note_lang(notes, current_note_idx, note_lang.value)
        Notes.save_notes(notes)
        note_error.value = "Saved!"
        note_error.color = ft.Colors.GREEN
        page.update()

    def on_text_change(e):
        lang = note_lang.value or "cz"
        preds = Notes.get_predictions(note_editor.value, lang)
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
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=4,
                ),
                note_actions_row,
            ], spacing=6, expand=True),
        ], expand=True),
    ], spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 7: Lunch Menu
    # ═══════════════════════════════════════════════════════
    lunch_error = ft.Text("", size=12, color=ft.Colors.RED)
    lunch_display = ft.Column(spacing=8)
    lunch_loading = ft.Text("Loading menu...", size=13, color=ft.Colors.GREY_600)

    def load_lunch(e=None):
        lunch_loading.visible = True
        lunch_error.value = ""
        lunch_display.controls.clear()
        page.update()

        menu = fetch_lunch_menu()

        lunch_loading.visible = False

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
                    day_items.append(ft.Text(meal["name"], size=13, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY))
                for i, item in enumerate(meal["items"]):
                    if i == 0:
                        icon = ft.Icons.SOUP_KITCHEN
                        color = ft.Colors.ORANGE
                    elif i == 1:
                        icon = ft.Icons.DINNER_DINING
                        color = ft.Colors.BROWN
                    else:
                        icon = ft.Icons.RICE_BOWL
                        color = ft.Colors.GREEN_700
                    day_items.append(
                        ft.Row([
                            ft.Icon(icon, size=12, color=color),
                            ft.Text(item, size=12),
                        ], spacing=6)
                    )
            if not day_items:
                day_items.append(ft.Text("No items listed", size=12, color=ft.Colors.GREY_500))

            lunch_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(day_label, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY),
                    ] + day_items, spacing=3),
                    padding=8,
                    border_radius=8,
                    bgcolor="#1F000000",
                )
            )

        page.update()

    load_lunch()

    lunch_page_content = ft.Column([
        section("Lunch Menu (Jídelníček)"),
        sub("Daily lunch options from stravovani.sspbrno.cz"),
        ft.Row([btn("Refresh", load_lunch)]),
        lunch_loading,
        lunch_error,
        lunch_display,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 8: EduPage Dashboard
    # ═══════════════════════════════════════════════════════
    edu_subdomain = ft.TextField(label="School subdomain", width=180, content_padding=8)
    edu_user = ft.TextField(label="Username", width=180, content_padding=8)
    edu_pass = ft.TextField(label="Password", width=180, password=True, can_reveal_password=True, content_padding=8)
    edu_error = ft.Text("", size=12, color=ft.Colors.RED)
    edu_status = ft.Text("", size=13, color=ft.Colors.GREEN)
    edu_session: EduSession | None = None
    edu_content = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    edu_remember = ft.Checkbox(label="Remember credentials", value=False)

    # Load saved credentials if any
    saved = load_credentials()
    if saved and saved["subdomain"]:
        edu_subdomain.value = saved["subdomain"]
        edu_user.value = saved["username"]
        edu_pass.value = saved["password"]
        edu_remember.value = True

    def edu_login(e):
        nonlocal edu_session
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

        # Save or clear credentials based on checkbox
        if edu_remember.value:
            save_credentials(sub, user, pw)
        else:
            clear_credentials()

        edu_session = EduSession(sub, user, pw)
        result = edu_session.login()
        if not result["success"]:
            edu_error.value = result["message"]
            page.update()
            return

        edu_status.value = "Logged in! Loading data..."
        page.update()

        # Fetch all data
        grades = edu_session.get_grades()
        timetable = edu_session.get_timetable()
        homework = edu_session.get_homework()
        attendance = edu_session.get_attendance()
        tests = edu_session.get_tests()
        class_avgs = edu_session.get_class_averages()
        subs = edu_session.get_substitutions()

        edu_content.controls.clear()

        # Grades section with integrated average calc
        edu_content.controls.append(section("Grades"))
        if grades["success"]:
            total_sum = 0
            total_w = 0
            for subj in grades["subjects"]:
                subj_items = []
                for g in subj["grades"]:
                    grade_val = g["grade"]
                    weight = g.get("weight", 1)
                    try:
                        gv = float(grade_val)
                        total_sum += gv * weight
                        total_w += weight
                    except (ValueError, TypeError):
                        pass
                    subj_items.append(ft.Text(f"  {grade_val} (w:{weight}) - {g.get('date','')} {g.get('title','')}", size=12))

                edu_content.controls.append(ft.Text(subj["name"], size=14, weight=ft.FontWeight.W_600))
                edu_content.controls.extend(subj_items)

            # Integrated weighted average
            if total_w > 0:
                avg = total_sum / total_w
                edu_content.controls.append(
                    ft.Text(f"Your weighted average: {avg:.2f}", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
                )

            # Class comparison
            if class_avgs["success"]:
                edu_content.controls.append(ft.Divider())
                edu_content.controls.append(section("Class Comparison"))
                for subj_name, class_avg in class_avgs["averages"].items():
                    edu_content.controls.append(
                        ft.Text(f"{subj_name}: class avg {class_avg:.2f}", size=13)
                    )
        else:
            edu_content.controls.append(ft.Text(grades["message"], size=13, color=ft.Colors.GREY_500))

        # Timetable
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Timetable"))
        if timetable["success"]:
            for day in timetable["days"]:
                edu_content.controls.append(ft.Text(day["date"], size=14, weight=ft.FontWeight.W_600))
                for lesson in day["lessons"]:
                    edu_content.controls.append(
                        ft.Text(f"  {lesson.get('hour','')}  {lesson.get('subject','')}  |  {lesson.get('teacher','')}  |  {lesson.get('room','')}", size=12)
                    )
        else:
            edu_content.controls.append(ft.Text(timetable["message"], size=13, color=ft.Colors.GREY_500))

        # Homework
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Homework"))
        if homework["success"]:
            for hw in homework["assignments"]:
                status_icon = ft.Icons.CHECK_CIRCLE if hw["completed"] else ft.Icons.PENDING
                edu_content.controls.append(
                    ft.Row([
                        ft.Icon(status_icon, size=14, color=ft.Colors.GREEN if hw["completed"] else ft.Colors.ORANGE),
                        ft.Text(f"{hw['subject']}: {hw['title']} (due: {hw['due']})", size=13),
                    ], spacing=8)
                )
        else:
            edu_content.controls.append(ft.Text(homework["message"], size=13, color=ft.Colors.GREY_500))

        # Attendance
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Attendance"))
        if attendance["success"]:
            s = attendance["summary"]
            edu_content.controls.append(
                ft.Text(f"Attendance: {s['percentage']}%  |  Present: {s['present']}  |  Absent: {s['absent']}  |  Late: {s['late']}  |  Excused: {s['excused']}",
                        size=13, weight=ft.FontWeight.W_600)
            )
        else:
            edu_content.controls.append(ft.Text(attendance["message"], size=13, color=ft.Colors.GREY_500))

        # Tests
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Upcoming Tests"))
        if tests["success"]:
            for t in tests["tests"]:
                edu_content.controls.append(
                    ft.Text(f"{t['subject']}: {t['title']} on {t['date']} ({t.get('type','')})", size=13)
                )
        else:
            edu_content.controls.append(ft.Text(tests["message"], size=13, color=ft.Colors.GREY_500))

        # Substitutions
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Substitutions"))
        if subs["success"]:
            for s_item in subs["substitutions"]:
                edu_content.controls.append(
                    ft.Text(f"{s_item['date']} Hr.{s_item['hour']}: {s_item['title']} [{s_item['action']}] {s_item['class']}", size=12)
                )
        else:
            edu_content.controls.append(ft.Text(subs["message"], size=13, color=ft.Colors.GREY_500))

        edu_status.value = "Data loaded."
        page.update()

    edu_page_content = ft.Column([
        section("EduPage Dashboard"),
        sub("Enter your EduPage credentials to sync grades, timetable, homework, attendance, tests, and substitutions."),
        ft.Row([edu_subdomain, edu_user, edu_pass, btn("Login", edu_login, primary=False)]),
        edu_remember,
        edu_error,
        edu_status,
        edu_content,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # ═══════════════════════════════════════════════════════
    # TAB 9: Scientific Calculator
    # ═══════════════════════════════════════════════════════


    # ═══════════════════════════════════════════════════════
    # TAB 10: Wolfram Alpha
    # ═══════════════════════════════════════════════════════
    wolf_api_key = [WolframAlpha.load_api_key()]  # mutable container
    wolf_query_history = [WolframAlpha.get_query_history()]  # mutable container
    wolf_current_result = [{"simple": [], "detailed": []}]  # mutable container
    wolf_view_mode = ["simple"]  # "simple" or "detailed"
    
    wolf_status_row = ft.Row([ft.Icon(ft.Icons.CLOUD_OFF, size=20, color=ft.Colors.RED)], spacing=0)
    wolf_status_text = ft.Text("Not logged in", size=12, color=ft.Colors.RED)
    wolf_error = ft.Text("", size=12, color=ft.Colors.RED)
    wolf_api_input = ft.TextField(label="API Key", width=250, password=True, can_reveal_password=True, content_padding=8)
    wolf_query_input = ft.TextField(label="Ask Wolfram Alpha...", width=400, content_padding=8)
    wolf_assumptions_input = ft.TextField(label="Assumptions (comma-separated, optional)", width=300, content_padding=8, visible=False)
    wolf_result_display = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    wolf_history_list = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
    
    def wolf_update_status():
        """Update login status display."""
        if wolf_api_key[0]:
            wolf_status_row.controls[0] = ft.Icon(ft.Icons.CLOUD_DONE, size=20, color=ft.Colors.GREEN)
            wolf_status_text.value = "Logged in"
            wolf_status_text.color = ft.Colors.GREEN
        else:
            wolf_status_row.controls[0] = ft.Icon(ft.Icons.CLOUD_OFF, size=20, color=ft.Colors.RED)
            wolf_status_text.value = "Not logged in"
            wolf_status_text.color = ft.Colors.RED
        page.update()
    
    def wolf_open_portal(e):
        """Open API portal in browser."""
        wolf_error.value = ""
        if WolframAlpha.open_api_portal():
            wolf_error.value = "Opened API portal in browser. Copy your API key and paste it below."
            wolf_error.color = ft.Colors.BLUE
        else:
            wolf_error.value = "Could not open browser. Visit https://products.wolframalpha.com/api/"
            wolf_error.color = ft.Colors.ORANGE
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
        
        # Validate key
        if WolframAlpha.validate_api_key(clipboard_text):
            wolf_api_key[0] = clipboard_text
            WolframAlpha.save_api_key(clipboard_text)
            wolf_error.value = "API key validated and saved! ✓"
            wolf_error.color = ft.Colors.GREEN
            wolf_update_status()
        else:
            wolf_error.value = "Invalid API key. Please try again."
            wolf_error.color = ft.Colors.RED
            wolf_api_key[0] = None
            wolf_update_status()
        
        page.update()
    
    def wolf_forget_key(e):
        """Clear saved API key."""
        wolf_api_key[0] = None
        wolf_api_input.value = ""
        WolframAlpha.clear_api_key()
        wolf_error.value = "API key forgotten."
        wolf_error.color = ft.Colors.ORANGE
        wolf_update_status()
        page.update()
    
    def wolf_validate_manual_key(e):
        """Validate manually entered API key."""
        wolf_error.value = ""
        input_text = wolf_api_input.value.strip()
        
        if not input_text:
            wolf_error.value = "Please enter an API key."
            wolf_error.color = ft.Colors.ORANGE
            page.update()
            return
        
        # Validate key
        if WolframAlpha.validate_api_key(input_text):
            wolf_api_key[0] = input_text
            WolframAlpha.save_api_key(input_text)
            wolf_error.value = "API key validated and saved! ✓"
            wolf_error.color = ft.Colors.GREEN
            wolf_update_status()
        else:
            wolf_error.value = "Invalid API key. Please check and try again."
            wolf_error.color = ft.Colors.RED
            wolf_api_key[0] = None
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
        
        if not wolf_api_key[0]:
            wolf_error.value = "Please log in first."
            page.update()
            return
        
        # Parse assumptions
        assumptions = []
        if wolf_assumptions_input.value.strip():
            assumptions = [a.strip() for a in wolf_assumptions_input.value.split(",")]
        
        # Query
        result = WolframAlpha.query(wolf_query_input.value, wolf_api_key[0], assumptions)
        
        if not result["success"]:
            wolf_error.value = result["message"]
            wolf_error.color = ft.Colors.RED
            page.update()
            return
        
        wolf_current_result[0] = result["results"]
        wolf_error.value = result["message"]
        wolf_error.color = ft.Colors.GREEN
        
        # Display results
        wolf_display_results()
        
        # Save to history
        WolframAlpha.save_query_to_history(wolf_query_input.value, result)
        wolf_refresh_history()
        
        page.update()
    
    def wolf_display_results():
        """Display current results based on view mode."""
        wolf_result_display.controls.clear()
        
        if wolf_view_mode[0] == "simple":
            results = wolf_current_result[0].get("simple", [])
            for i, res_text in enumerate(results):
                wolf_result_display.controls.append(
                    ft.Container(
                        content=ft.Text(res_text, size=13, selectable=True),
                        padding=10,
                        border_radius=6,
                        bgcolor="#1F000000",
                        border=ft.border.all(1, ft.Colors.GREY_400)
                    )
                )
        else:  # detailed
            detailed = wolf_current_result[0].get("detailed", [])
            for pod in detailed:
                pod_content = [
                    ft.Text(pod["title"], size=13, weight=ft.FontWeight.W_600, color=ft.Colors.PRIMARY)
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
                        border=ft.border.all(1, ft.Colors.BLUE_300)
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
        history = wolf_query_history[0]
        if idx < len(history):
            item = history[idx]
            wolf_current_result[0] = item.get("results", {"simple": [], "detailed": []})
            wolf_display_results()
            page.update()
    
    def wolf_refresh_history():
        """Rebuild history sidebar."""
        wolf_query_history[0] = WolframAlpha.get_query_history()
        wolf_history_list.controls.clear()
        
        for i, item in enumerate(wolf_query_history[0]):
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
        WolframAlpha.clear_history()
        wolf_refresh_history()
        wolf_error.value = "History cleared."
        wolf_error.color = ft.Colors.ORANGE
        page.update()
    
    view_btn = btn("📊 Detailed", wolf_toggle_view)
    wolf_update_status()
    wolf_refresh_history()
    
    wolf_page_content = ft.Column([
        section("Wolfram Alpha Query"),
        
        # Login section
        ft.Row([
            ft.Icon(ft.Icons.LOCK_OPEN, size=20, color=ft.Colors.BLUE),
            ft.Column([
                ft.Text("Log in to Wolfram Alpha", size=13, weight=ft.FontWeight.W_600),
                ft.Text("Click 'Open Portal' → log in → click 'Get an App ID' → fill out and select 'Full Results API' → copy App ID → click 'Paste'", size=11, color=ft.Colors.GREY_600),
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
                border=ft.border.all(1, ft.Colors.GREY_400),
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
                    border=ft.border.all(1, ft.Colors.GREY_300),
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
        grade_page_content,
        subnet_page_content,
        base_page_content,
        bool_page_content,
        unit_page_content,
        fc_page_content,
        notes_page_content,
        lunch_page_content,
        edu_page_content,
        #sci_page_content,
        wolf_page_content,
    ])

    nav = ft.Tabs(
        length=11,
        selected_index=0,
        expand=True,
        content=ft.Column([
            ft.TabBar(tabs=[
                ft.Tab(label="Grades"),
                ft.Tab(label="Subnets"),
                ft.Tab(label="Base Calc"),
                ft.Tab(label="Bool Alg"),
                ft.Tab(label="Units"),
                ft.Tab(label="Flashcards"),
                ft.Tab(label="Notepad"),
                ft.Tab(label="Lunch"),
                ft.Tab(label="EduPage"),
                #ft.Tab(label="Sci Calc"),
                ft.Tab(label="Wolfram"),
            ]),
            ft.Container(content=tab_bar_view, expand=True),
        ], spacing=0, expand=True),
    )

    page.add(header, nav)

ft.run(main)