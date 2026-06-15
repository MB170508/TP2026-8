"""EduPage Dashboard tab."""

import flet as ft
from managers.EduPage import EduPageManager
from ui.components.colors import (
    ERROR_COLOR,
    SUCCESS_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    GREY_500_COLOR,
    BLUE_COLOR,
    ORANGE_COLOR,
    AMBER_COLOR,
)
from ui.components.factories import btn, section, sub


def create_edupage_tab(page: ft.Page) -> ft.Column:
    """Create EduPage Dashboard tab.

    Login to EduPage, view grades, timetable, homework, and manage
    manual grade entries with weighted average calculation.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete EduPage dashboard tab UI
    """
    # ── Initialize ──────────────────────────────────
    edu_manager = EduPageManager()
    edu_subdomain = ft.TextField(label="School subdomain", width=180, content_padding=8)
    edu_user = ft.TextField(label="Username", width=180, content_padding=8)
    edu_pass = ft.TextField(
        label="Password",
        width=180,
        password=True,
        can_reveal_password=True,
        content_padding=8,
    )
    edu_error = ft.Text("", size=12, color=ERROR_COLOR)
    edu_status = ft.Text("", size=13, color=SUCCESS_COLOR)
    edu_content = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    edu_remember = ft.Checkbox(label="Remember credentials", value=False)

    # Manual grade inputs
    manual_subject_input = ft.TextField(label="Subject", width=150, content_padding=8)
    manual_grade_input = ft.TextField(
        label="Grade (1-5)",
        width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=8,
    )
    manual_weight_input = ft.TextField(
        label="Weight",
        width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=8,
    )
    manual_grades_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    target_input = ft.TextField(
        label="Target avg (1=best)",
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=8,
    )
    target_result = ft.Text("", size=13)

    # Load saved credentials if any
    saved = edu_manager.load_saved_credentials()
    if saved:
        edu_subdomain.value = saved["subdomain"]
        edu_user.value = saved["username"]
        edu_pass.value = saved["password"]
        edu_remember.value = True

    # ── Event Handlers ──────────────────────────────
    def build_manual_grades():
        """Build and display manual grades."""
        manual_grades_display.controls.clear()
        manual_grades = edu_manager.get_manual_grades()["grades"]
        for subject, grades_list in manual_grades.items():
            subject_container = ft.Column(
                [
                    ft.Text(subject, size=14, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR)
                ],
                spacing=2,
            )
            for i, (g, w) in enumerate(grades_list):
                subject_container.controls.append(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.STAR, size=14, color=AMBER_COLOR),
                            ft.Text(f"Grade: {g} × Weight: {w}", size=13),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=14,
                                tooltip="Remove",
                                on_click=lambda e, s=subject, idx=i: remove_manual_grade(
                                    s, idx
                                ),
                            ),
                        ],
                        spacing=8,
                    )
                )
            manual_grades_display.controls.append(subject_container)

    def add_manual_grade(e):
        """Add a manual grade."""
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
        """Remove a manual grade."""
        result = edu_manager.remove_manual_grade(subject, index)
        if result["success"]:
            build_manual_grades()
            target_result.value = ""
        else:
            edu_error.value = result["message"]
        page.update()

    def calc_target(e):
        """Calculate target grade needed."""
        target_result.value = ""
        try:
            target = float(target_input.value)
        except (ValueError, TypeError):
            target_result.value = "Enter a valid target average."
            page.update()
            return

        # Get all grades for calculation
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
        """Login to EduPage and load dashboard (show cached data while loading)."""
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

        # Show status and try to display cached data first
        edu_status.value = "Loading data..."
        page.update()

        # Try to show cached data while fetching new data
        cached = edu_manager.get_cached_dashboard_data()
        if cached and cached.get("success"):
            edu_status.value = "Loading... (showing cached data)"
            display_dashboard_data(cached)
            page.update()

        # Get fresh integrated dashboard data
        dashboard = edu_manager.get_dashboard_data()
        if not dashboard["success"]:
            edu_error.value = dashboard["message"]
            page.update()
            return

        # Update with fresh data
        edu_status.value = dashboard["message"]
        display_dashboard_data(dashboard)
        page.update()

    def display_dashboard_data(dashboard):
        """Display dashboard data in the content area."""
        edu_content.controls.clear()

        # Grades section
        edu_content.controls.append(section("Grades & Averages"))
        if dashboard["grades"]["success"]:
            overall_avg = dashboard["grades"]["overall_average"]
            if overall_avg > 0:
                edu_content.controls.append(
                    ft.Text(
                        f"Overall weighted average: {overall_avg:.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_COLOR,
                    )
                )

            for subj in dashboard["grades"]["subjects"]:
                subj_items = []
                for g in subj["grades"]:
                    source_icon = (
                        ft.Icons.CLOUD
                        if g.get("source") != "manual"
                        else ft.Icons.EDIT
                    )
                    subj_items.append(
                        ft.Row(
                            [
                                ft.Icon(
                                    source_icon,
                                    size=12,
                                    color=BLUE_COLOR
                                    if g.get("source") != "manual"
                                    else ORANGE_COLOR,
                                ),
                                ft.Text(
                                    f"{g['grade']} (w:{g.get('weight',1)}) - {g.get('date','')} {g.get('title','')}",
                                    size=12,
                                ),
                            ],
                            spacing=4,
                        )
                    )

                subj_col = ft.Column(
                    [
                        ft.Text(subj["name"], size=14, weight=ft.FontWeight.W_600),
                    ]
                    + subj_items,
                    spacing=2,
                )

                if (
                    "weighted_average" in subj
                    and subj["weighted_average"] > 0
                ):
                    subj_col.controls.append(
                        ft.Text(
                            f"Average: {subj['weighted_average']:.2f}",
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=SECONDARY_COLOR,
                        )
                    )

                edu_content.controls.append(subj_col)

            # Class comparison
            if dashboard["class_averages"]["success"]:
                edu_content.controls.append(ft.Divider())
                edu_content.controls.append(section("Class Comparison"))
                for subj_name, class_avg in dashboard["class_averages"][
                    "averages"
                ].items():
                    edu_content.controls.append(
                        ft.Text(f"{subj_name}: class avg {class_avg:.2f}", size=13)
                    )
        else:
            edu_content.controls.append(
                ft.Text(
                    dashboard["grades"]["message"],
                    size=13,
                    color=GREY_500_COLOR,
                )
            )

        # Timetable
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Timetable"))
        if dashboard["timetable"]["success"]:
            for day in dashboard["timetable"]["days"]:
                edu_content.controls.append(
                    ft.Text(day["date"], size=14, weight=ft.FontWeight.W_600)
                )
                for lesson in day["lessons"]:
                    edu_content.controls.append(
                        ft.Text(
                            f"  {lesson.get('hour','')}  {lesson.get('subject','')}  |  {lesson.get('teacher','')}  |  {lesson.get('room','')}",
                            size=12,
                        )
                    )
        else:
            edu_content.controls.append(
                ft.Text(
                    dashboard["timetable"]["message"],
                    size=13,
                    color=GREY_500_COLOR,
                )
            )

        # Homework
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Homework"))
        if dashboard["homework"]["success"]:
            for hw in dashboard["homework"]["assignments"]:
                status_icon = (
                    ft.Icons.CHECK_CIRCLE if hw["completed"] else ft.Icons.PENDING
                )
                edu_content.controls.append(
                    ft.Row(
                        [
                            ft.Icon(
                                status_icon,
                                size=14,
                                color=SUCCESS_COLOR
                                if hw["completed"]
                                else ORANGE_COLOR,
                            ),
                            ft.Text(
                                f"{hw['subject']}: {hw['title']} (due: {hw['due']})",
                                size=13,
                            ),
                        ],
                        spacing=8,
                    )
                )
        else:
            edu_content.controls.append(
                ft.Text(
                    dashboard["homework"]["message"],
                    size=13,
                    color=GREY_500_COLOR,
                )
            )

        # Tests
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Upcoming Tests"))
        if dashboard["tests"]["success"]:
            for t in dashboard["tests"]["tests"]:
                edu_content.controls.append(
                    ft.Text(
                        f"{t['subject']}: {t['title']} on {t['date']} ({t.get('type','')})",
                        size=13,
                    )
                )
        else:
            edu_content.controls.append(
                ft.Text(
                    dashboard["tests"]["message"],
                    size=13,
                    color=GREY_500_COLOR,
                )
            )

        # Substitutions
        edu_content.controls.append(ft.Divider())
        edu_content.controls.append(section("Substitutions"))
        if dashboard["substitutions"]["success"]:
            for s_item in dashboard["substitutions"]["substitutions"]:
                edu_content.controls.append(
                    ft.Text(
                        f"{s_item['date']} Hr.{s_item['hour']}: {s_item['title']} [{s_item['action']}] {s_item['class']}",
                        size=12,
                    )
                )
        else:
            edu_content.controls.append(
                ft.Text(
                    dashboard["substitutions"]["message"],
                    size=13,
                    color=GREY_500_COLOR,
                )
            )

        edu_status.value = "Data loaded."
        page.update()

    # Build initial manual grades display
    build_manual_grades()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
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
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
