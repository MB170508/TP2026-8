"""Lunch Menu tab."""

import flet as ft
from Lunch import LunchMenuManager
from ui.components.colors import (
    ERROR_COLOR,
    GREY_COLOR,
    GREY_500_COLOR,
    ORANGE_COLOR,
    BROWN_COLOR,
    GREEN_700_COLOR,
    PRIMARY_COLOR,
    CARD_BACKGROUND,
)
from ui.components.factories import btn, section, sub
from ui.components.error_display import set_error


def create_lunch_tab(page: ft.Page) -> ft.Column:
    """Create Lunch Menu tab.

    Display daily lunch menu from stravovani.sspbrno.cz with caching.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete lunch menu tab UI
    """
    # ── Initialize ──────────────────────────────────
    lunch_manager = LunchMenuManager()
    lunch_error = ft.Text("", size=12, color=ERROR_COLOR)
    lunch_display = ft.Column(spacing=8)
    lunch_loading = ft.Text("Loading menu...", size=13, color=GREY_COLOR)
    lunch_status = ft.Text("", size=12, color=GREY_500_COLOR)

    # ── Event Handlers ──────────────────────────────
    def display_lunch_menu(menu):
        """Display lunch menu in lunch_display column."""
        lunch_display.controls.clear()
        for day in menu:
            if not day["meals"]:
                continue
            day_label = day["day_name"] or day["date"] or "Unknown day"
            day_items = []
            for meal in day["meals"]:
                if meal["name"]:
                    day_items.append(
                        ft.Text(
                            meal["name"],
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=PRIMARY_COLOR,
                        )
                    )
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
                        ft.Row(
                            [
                                ft.Icon(icon, size=12, color=color),
                                ft.Text(item, size=12),
                            ],
                            spacing=6,
                        )
                    )
            if not day_items:
                day_items.append(
                    ft.Text(
                        "No items listed", size=12, color=GREY_500_COLOR
                    )
                )

            lunch_display.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                day_label,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=PRIMARY_COLOR,
                            ),
                        ]
                        + day_items,
                        spacing=3,
                    ),
                    padding=8,
                    border_radius=8,
                    bgcolor=CARD_BACKGROUND,
                )
            )

    def load_lunch(e=None):
        """Fetch and display fresh lunch menu. On error, fallback to cache."""
        lunch_loading.visible = True
        lunch_error.value = ""
        lunch_status.value = ""
        lunch_display.controls.clear()
        page.update()

        result = lunch_manager.fetch_menu()
        lunch_loading.visible = False

        if not result["success"]:
            # Error during fetch; try fallback to cache
            cached = lunch_manager.get_cached_menu()
            if cached["success"]:
                display_lunch_menu(cached["menu"])
                set_error(
                    lunch_error,
                    f"⚠️ Using cached menu (failed to fetch: {result['message']})",
                    color=ORANGE_COLOR,
                    page=page,
                )
                lunch_status.value = (
                    f"Cached at {lunch_manager.last_fetch_time.strftime('%H:%M') if lunch_manager.last_fetch_time else 'unknown'}"
                )
            else:
                set_error(lunch_error, result["message"], page=page)
            page.update()
            return

        menu = result["menu"]
        if not menu:
            set_error(lunch_error, "No menu data found.", page=page)
            page.update()
            return

        display_lunch_menu(menu)
        lunch_status.value = (
            f"Menu updated at {lunch_manager.last_fetch_time.strftime('%H:%M')}"
        )
        page.update()

    def load_lunch_startup():
        """Load lunch menu on startup: show cache first, then fetch fresh."""
        # Show cached menu immediately if valid
        if lunch_manager.is_cache_valid() and lunch_manager.last_menu:
            display_lunch_menu(lunch_manager.last_menu)
            lunch_status.value = "Cached menu (fetching fresh...)"
            page.update()
            # Fetch fresh in background
            result = lunch_manager.fetch_menu()
            if result["success"] and result["menu"]:
                display_lunch_menu(result["menu"])
                lunch_status.value = (
                    f"Menu updated at {lunch_manager.last_fetch_time.strftime('%H:%M')}"
                )
            page.update()
        else:
            # No valid cache, fetch fresh
            load_lunch()

    # Load menu on startup
    load_lunch_startup()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Lunch Menu (Jídelníček)"),
            sub("Daily lunch options from stravovani.sspbrno.cz"),
            ft.Row([btn("Refresh", load_lunch)]),
            lunch_loading,
            lunch_status,
            lunch_error,
            lunch_display,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
