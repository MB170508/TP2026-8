"""Wolfram Alpha Query tab."""

import flet as ft
from WolframAlpha import WolframAlphaManager
from utilities.validators import validate_api_key
from ui.components.colors import (
    ERROR_COLOR,
    SUCCESS_COLOR,
    ORANGE_COLOR,
    BLUE_COLOR,
    BLUE_300_COLOR,
    GREY_COLOR,
    GREY_300_COLOR,
    GREY_400_COLOR,
    PRIMARY_COLOR,
    CARD_BACKGROUND,
)
from ui.components.factories import btn, section
from ui.components.error_display import set_error


def create_wolfram_tab(page: ft.Page) -> ft.Column:
    """Create Wolfram Alpha Query tab.

    Query Wolfram Alpha API with results display in simple or detailed view.
    Manages API key credentials and maintains query history.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete Wolfram Alpha tab UI
    """
    # ── Initialize ──────────────────────────────────
    wolf_manager = WolframAlphaManager()
    wolf_status_row = ft.Row(
        [ft.Icon(ft.Icons.CLOUD_OFF, size=20, color=ERROR_COLOR)], spacing=0
    )
    wolf_status_text = ft.Text("Not logged in", size=12, color=ERROR_COLOR)
    wolf_error = ft.Text("", size=12, color=ERROR_COLOR)
    wolf_loading = ft.Text("", size=12, color=GREY_COLOR)
    wolf_api_input = ft.TextField(
        label="API Key",
        width=250,
        password=True,
        can_reveal_password=True,
        content_padding=8,
    )
    wolf_query_input = ft.TextField(
        label="Ask Wolfram Alpha...", width=400, content_padding=8
    )
    wolf_assumptions_input = ft.TextField(
        label="Assumptions (comma-separated, optional)",
        width=300,
        content_padding=8,
        visible=False,
    )
    wolf_result_display = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    wolf_history_list = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
    wolf_view_mode = ["simple"]  # "simple" or "detailed"
    wolf_current_result = {"simple": [], "detailed": []}

    # ── Event Handlers ──────────────────────────────
    def validate_wolf_api_key(e):
        """Real-time validation for Wolfram Alpha API key."""
        if not e.control.value:
            wolf_error.value = ""
        else:
            is_valid, error_msg = validate_api_key(
                e.control.value, min_length=10
            )
            wolf_error.value = error_msg if not is_valid else ""
        page.update()

    wolf_api_input.on_change = validate_wolf_api_key

    def wolf_update_status():
        """Update login status display."""
        if wolf_manager.has_api_key():
            wolf_status_row.controls[0] = ft.Icon(
                ft.Icons.CLOUD_DONE, size=20, color=SUCCESS_COLOR
            )
            wolf_status_text.value = "Logged in"
            wolf_status_text.color = SUCCESS_COLOR
        else:
            wolf_status_row.controls[0] = ft.Icon(
                ft.Icons.CLOUD_OFF, size=20, color=ERROR_COLOR
            )
            wolf_status_text.value = "Not logged in"
            wolf_status_text.color = ERROR_COLOR
        page.update()

    def wolf_open_portal(e):
        """Open API portal in browser."""
        wolf_error.value = ""
        if wolf_manager.open_portal():
            wolf_error.value = (
                "Opened API portal in browser. Copy your API key and paste it below."
            )
            wolf_error.color = BLUE_COLOR
        else:
            wolf_error.value = (
                "Could not open browser. Visit https://products.wolframalpha.com/api/"
            )
            wolf_error.color = ORANGE_COLOR
        page.update()

    def wolf_paste_key(e):
        """Paste API key from clipboard and validate."""
        wolf_error.value = ""
        wolf_loading.value = ""
        try:
            import pyperclip

            clipboard_text = pyperclip.paste().strip()
        except Exception:
            set_error(
                wolf_error,
                "Could not access clipboard. Please paste manually.",
                page=page,
            )
            return

        if not clipboard_text:
            set_error(wolf_error, "Clipboard is empty.", page=page)
            return

        wolf_api_input.value = clipboard_text

        # Show loading and validate
        wolf_loading.value = "Validating API key..."
        page.update()

        result = wolf_manager.set_api_key(clipboard_text)
        wolf_loading.value = ""
        set_error(
            wolf_error,
            result["message"],
            SUCCESS_COLOR if result["success"] else ERROR_COLOR,
            page=page,
        )
        wolf_update_status()

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
        wolf_loading.value = ""
        input_text = wolf_api_input.value.strip()

        if not input_text:
            set_error(
                wolf_error,
                "Please enter an API key.",
                ORANGE_COLOR,
                page=page,
            )
            return

        # Show loading and validate
        wolf_loading.value = "Validating API key..."
        page.update()

        result = wolf_manager.set_api_key(input_text)
        wolf_loading.value = ""
        set_error(
            wolf_error,
            result["message"],
            SUCCESS_COLOR if result["success"] else ERROR_COLOR,
            page=page,
        )
        wolf_update_status()

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
            assumptions = [
                a.strip() for a in wolf_assumptions_input.value.split(",")
            ]

        # Query
        result = wolf_manager.query(wolf_query_input.value, assumptions)

        if not result["success"]:
            wolf_error.value = result["message"]
            wolf_error.color = ERROR_COLOR
            page.update()
            return

        nonlocal wolf_current_result
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
                        bgcolor=CARD_BACKGROUND,
                        border=ft.Border.all(1, GREY_400_COLOR),
                    )
                )
        else:  # detailed
            detailed = wolf_current_result.get("detailed", [])
            for pod in detailed:
                pod_content = [
                    ft.Text(
                        pod["title"],
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=PRIMARY_COLOR,
                    )
                ]
                for subpod in pod.get("subpods", []):
                    pod_content.append(
                        ft.Text(
                            subpod.get("text", ""), size=12, selectable=True
                        )
                    )

                wolf_result_display.controls.append(
                    ft.Container(
                        content=ft.Column(pod_content, spacing=4),
                        padding=10,
                        border_radius=6,
                        bgcolor=CARD_BACKGROUND,
                        border=ft.Border.all(1, BLUE_300_COLOR),
                    )
                )

    def wolf_toggle_view(e):
        """Toggle between simple and detailed view."""
        wolf_view_mode[0] = (
            "detailed" if wolf_view_mode[0] == "simple" else "simple"
        )
        view_btn.text = (
            "📊 Detailed"
            if wolf_view_mode[0] == "simple"
            else "📝 Simple"
        )
        wolf_display_results()
        page.update()

    def wolf_load_history(idx):
        """Load query from history."""
        history = wolf_manager.get_history()
        if idx < len(history):
            item = history[idx]
            nonlocal wolf_current_result
            wolf_current_result = item.get(
                "results", {"simple": [], "detailed": []}
            )
            wolf_display_results()
            page.update()

    def wolf_refresh_history():
        """Rebuild history sidebar."""
        history = wolf_manager.get_history()
        wolf_history_list.controls.clear()

        for i, item in enumerate(history):
            query_text = (
                item.get("query", "")[:50]
                + ("..." if len(item.get("query", "")) > 50 else "")
            )
            wolf_history_list.controls.append(
                ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(query_text, size=12),
                            trailing=ft.Icon(ft.Icons.HISTORY, size=14),
                            on_click=lambda e, idx=i: wolf_load_history(idx),
                            content_padding=4,
                        ),
                        ft.Divider(height=1),
                    ],
                    spacing=0,
                )
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

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Wolfram Alpha Query"),
            # Login section
            ft.Row(
                [
                    ft.Icon(ft.Icons.LOCK_OPEN, size=20, color=BLUE_COLOR),
                    ft.Column(
                        [
                            ft.Text(
                                "Log in to Wolfram Alpha",
                                size=13,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Text(
                                "Click 'Open Portal' → log in → click 'Get an App ID' → fill out and select 'Full Results API' → copy App ID → click 'Paste'",
                                size=11,
                                color=GREY_COLOR,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Row(
                [
                    btn("🌐 Open Portal", wolf_open_portal),
                    btn("📋 Paste Key", wolf_paste_key),
                    btn("✓ Validate", wolf_validate_manual_key),
                    btn("🗑️ Forget", wolf_forget_key),
                    ft.Row([wolf_status_row, wolf_status_text], spacing=6),
                ],
                spacing=8,
            ),
            wolf_api_input,
            wolf_error,
            wolf_loading,
            ft.Divider(),
            # Query section
            section("Query"),
            ft.Row(
                [
                    wolf_query_input,
                    btn("🔍 Evaluate", wolf_execute_query, primary=True),
                    view_btn,
                ],
                spacing=8,
            ),
            ft.Row([wolf_assumptions_input], spacing=8),
            # Results + History
            ft.Row(
                [
                    # Results (left, main)
                    ft.Container(
                        content=wolf_result_display,
                        expand=True,
                        border_radius=6,
                        border=ft.Border.all(1, GREY_400_COLOR),
                        padding=10,
                    ),
                    # History sidebar (right)
                    ft.Column(
                        [
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
                        ],
                        spacing=6,
                    ),
                ],
                spacing=12,
                expand=True,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
