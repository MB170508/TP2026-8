"""IT Toolbox - Educational utility application for networking and computation."""

import asyncio
import flet as ft

# Import tab creators
from ui.tabs.subnet_tab import create_subnet_tab
from ui.tabs.base_calc_tab import create_base_calc_tab
from ui.tabs.bool_alg_tab import create_bool_alg_tab
from ui.tabs.unit_converter_tab import create_unit_converter_tab
from ui.tabs.flashcards_tab import create_flashcards_tab
from ui.tabs.notepad_tab import create_notepad_tab
from ui.tabs.lunch_tab import create_lunch_tab
from ui.tabs.edupage_tab import create_edupage_tab
from ui.tabs.scientific_calc_tab import create_scientific_calc_tab
from ui.tabs.wolfram_tab import create_wolfram_tab

# Import UI components
from ui.components.colors import PRIMARY_COLOR
from ui.components.factories import btn

# Import infrastructure
from config import config_manager
from utilities.logger import init_logging, get_logger

# Initialize on startup
init_logging()
logger = get_logger(__name__)


def main(page: ft.Page):
    """Main application entry point."""
    page.title = "IT Toolbox"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 12
    page.spacing = 8
    page.window_width = 1100
    page.window_height = 850

    # ── Theme Mode Toggle ──────────────────────────
    _mode_cycle = [ft.ThemeMode.SYSTEM]

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

    # ── Header ──────────────────────────────────────
    header = ft.Row(
        [
            ft.Text("IT Toolbox", size=30, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            theme_icon,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # ── Create all tabs ──────────────────────────────
    tab_contents = [
        create_subnet_tab(page),
        create_base_calc_tab(page),
        create_bool_alg_tab(page),
        create_unit_converter_tab(page),
        create_flashcards_tab(page),
        create_notepad_tab(page),
        create_lunch_tab(page),
        create_edupage_tab(page),
        create_scientific_calc_tab(page),
        create_wolfram_tab(page),
    ]

    # ── Navigation ──────────────────────────────────
    tab_bar_view = ft.TabBarView(controls=tab_contents)

    nav = ft.Tabs(
        length=10,
        selected_index=0,
        expand=True,
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
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
                    ]
                ),
                ft.Container(content=tab_bar_view, expand=True),
            ],
            spacing=0,
            expand=True,
        ),
    )

    # ── Keyboard shortcuts ──────────────────────────
    def on_keyboard_event(e: ft.KeyboardEvent):
        if e.key == "L" and e.ctrl:  # Ctrl+L → Lunch
            nav.selected_index = 6
            page.update()
        elif e.key == "N" and e.ctrl:  # Ctrl+N → Notes
            nav.selected_index = 5
            page.update()
        elif e.key == "Q" and e.ctrl:  # Ctrl+Q → Wolfram Query
            nav.selected_index = 9
            page.update()
        elif e.key == "D" and e.ctrl:  # Ctrl+D → Decks/Flashcards
            nav.selected_index = 4
            page.update()

    page.on_keyboard_event = on_keyboard_event

    # ── Assemble page ──────────────────────────────
    page.add(header, nav)


if __name__ == "__main__":
    ft.run(main)
