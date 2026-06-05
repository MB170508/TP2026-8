"""Flashcards Quiz tab."""

import flet as ft
from Flashcards import FlashcardManager
from ui.components.colors import (
    ERROR_COLOR,
    SUCCESS_COLOR,
    TEAL_COLOR,
    GREY_COLOR,
    GREY_500_COLOR,
    CARD_BACKGROUND,
)
from ui.components.factories import btn, section


def create_flashcards_tab(page: ft.Page) -> ft.Column:
    """Create Flashcards Quiz tab.

    Manage flashcard decks and run quiz mode with flip-to-reveal cards.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete flashcards tab UI
    """
    # ── Initialize ──────────────────────────────────
    flashcard_manager = FlashcardManager()
    fc_deck_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    fc_deck_selector = ft.Dropdown(label="Select Deck", width=200, content_padding=8)
    fc_new_deck_name = ft.TextField(
        label="New Deck Name", width=180, content_padding=8
    )
    fc_card_front = ft.TextField(label="Front", width=180, content_padding=8)
    fc_card_back = ft.TextField(label="Back", width=180, content_padding=8)
    fc_deck_error = ft.Text("", size=12, color=ERROR_COLOR)
    fc_card_display = ft.Column(spacing=8)
    fc_quiz_progress = ft.Text("", size=12)

    # ── Event Handlers ──────────────────────────────
    def refresh_deck_list():
        """Refresh deck list display and selector."""
        fc_deck_list.controls.clear()
        fc_deck_selector.options.clear()
        deck_names = flashcard_manager.get_deck_names()
        for name in deck_names:
            info = flashcard_manager.get_deck_info(name)
            count = info["card_count"]
            fc_deck_list.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LAYERS, size=14, color=TEAL_COLOR),
                        ft.Text(f"{name} ({count})", size=13),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_size=14,
                            on_click=lambda e, n=name: delete_deck_handler(n),
                        ),
                    ],
                    spacing=8,
                )
            )
            fc_deck_selector.options.append(ft.dropdown.Option(name))
        if deck_names:
            fc_deck_selector.value = deck_names[0]

    def create_deck_handler(e):
        """Create a new flashcard deck."""
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
        """Delete a flashcard deck."""
        result = flashcard_manager.delete_deck(name)
        if not result["success"]:
            fc_deck_error.value = result["message"]
        refresh_deck_list()
        fc_card_display.controls.clear()
        fc_quiz_progress.value = ""
        page.update()

    def add_card_handler(e):
        """Add a card to the selected deck."""
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
        """Start a quiz session."""
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
        """Display the current card in quiz mode."""
        fc_card_display.controls.clear()
        card_result = flashcard_manager.get_current_card()
        if not card_result["success"]:
            if "completed" in card_result["message"].lower():
                fc_card_display.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "🎉 Quiz Complete!",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=SUCCESS_COLOR,
                                ),
                                ft.Text("Great job studying!", size=14),
                                ft.Row(
                                    [
                                        btn("Restart Quiz", restart_quiz_handler),
                                        btn("New Quiz", start_quiz_handler),
                                    ],
                                    spacing=10,
                                ),
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                        border_radius=10,
                        bgcolor=CARD_BACKGROUND,
                        alignment=ft.Alignment.CENTER,
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
                    content=ft.Column(
                        [
                            ft.Text("Front", size=11, color=GREY_COLOR),
                            ft.Text(front_text, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                "Click to reveal answer",
                                size=12,
                                color=GREY_500_COLOR,
                            ),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    border_radius=10,
                    bgcolor=CARD_BACKGROUND,
                    alignment=ft.Alignment.CENTER,
                )
            )
            fc_card_display.controls.append(
                ft.Row(
                    [
                        btn("Flip Card", flip_card_handler, primary=True),
                        btn("Next Card", next_card_handler),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                )
            )
        else:
            # Show both front and back
            fc_card_display.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Front", size=11, color=GREY_COLOR),
                            ft.Text(front_text, size=18, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text("Back", size=11, color=GREY_COLOR),
                            ft.Text(back_text, size=16),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    border_radius=10,
                    bgcolor=CARD_BACKGROUND,
                    alignment=ft.Alignment.CENTER,
                )
            )
            fc_card_display.controls.append(
                ft.Row(
                    [
                        btn("Next Card", next_card_handler, primary=True),
                        btn("Restart Quiz", restart_quiz_handler),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                )
            )
        page.update()

    def flip_card_handler(e):
        """Flip card to show answer."""
        result = flashcard_manager.flip_card()
        if result["success"]:
            show_current_card()

    def next_card_handler(e):
        """Move to next card."""
        result = flashcard_manager.next_card()
        if result["success"]:
            show_current_card()
        else:
            show_current_card()  # This will show completion message

    def restart_quiz_handler(e):
        """Restart quiz from beginning."""
        result = flashcard_manager.restart_quiz()
        if result["success"]:
            show_current_card()
        else:
            fc_deck_error.value = result["message"]
            page.update()

    refresh_deck_list()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Flashcards"),
            ft.Row([fc_new_deck_name, btn("Create", create_deck_handler)]),
            ft.Row([fc_card_front, fc_card_back, btn("Add", add_card_handler)]),
            fc_deck_error,
            ft.Row([fc_deck_selector, btn("Quiz", start_quiz_handler, primary=True)]),
            fc_quiz_progress,
            ft.Container(content=fc_deck_list, expand=True),
            fc_card_display,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )
