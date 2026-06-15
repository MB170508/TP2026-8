"""Notepad with word prediction tab."""

import flet as ft
from managers.Notes import NotesManager
from ui.components.colors import (
    ERROR_COLOR,
    SUCCESS_COLOR,
    PRIMARY_COLOR,
    ON_SURFACE_COLOR,
    GREY_500_COLOR,
    GREY_300_COLOR,
)
from ui.components.factories import btn, section, sub


def create_notepad_tab(page: ft.Page) -> ft.Column:
    """Create Notepad tab with word prediction.

    Create and edit notes with language-specific word predictions.
    Supports Czech (CZ) and English (EN) prediction.

    Args:
        page: Flet page instance

    Returns:
        ft.Column containing complete notepad tab UI
    """
    # ── Initialize ──────────────────────────────────
    notes_manager = NotesManager()
    notes_list = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
    notes_list_header = ft.Text(
        "Notes", size=13, weight=ft.FontWeight.W_600, visible=False
    )
    note_title_input = ft.TextField(
        label="Note title", width=180, content_padding=8
    )
    editor_frame = ft.Row(scroll=ft.ScrollMode.AUTO)
    note_editor = ft.TextField(
        label="Write...",
        multiline=True,
        min_lines=8,
        expand=True,
    )
    editor_frame.controls.append(note_editor)
    note_lang = ft.Dropdown(
        options=[ft.dropdown.Option("cz"), ft.dropdown.Option("en")],
        value="cz",
        width=80,
        label="Lang",
        content_padding=8,
    )
    predictions_row = ft.Row(spacing=6)
    suggestions_label = ft.Text(
        "Suggestions:", size=11, color=GREY_500_COLOR, visible=False
    )
    note_error = ft.Text("", size=12, color=ERROR_COLOR)
    note_info = ft.Text("", size=12, color=GREY_500_COLOR)
    note_actions_row = None  # created below after all handlers defined
    note_editor.visible = False

    # ── Event Handlers ──────────────────────────────
    def refresh_notes_list():
        """Refresh notes list display."""
        notes_list.controls.clear()
        all_notes = notes_manager.get_all_notes()
        notes_list_header.visible = len(all_notes) > 0
        for i, n in enumerate(all_notes):
            current = notes_manager.get_current_note()
            is_current = (
                current.get("success")
                and current["note"]["title"] == n["title"]
            )
            color = PRIMARY_COLOR if is_current else ON_SURFACE_COLOR
            weight = (
                ft.FontWeight.W_600 if is_current else ft.FontWeight.W_400
            )
            notes_list.controls.append(
                ft.ListTile(
                    title=ft.Text(n["title"], size=13, color=color, weight=weight),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINED,
                        icon_size=16,
                        on_click=lambda e, idx=i: delete_note_handler(idx),
                    ),
                    on_click=lambda e, idx=i: load_note(idx),
                    content_padding=4,
                )
            )

    def create_note_handler(e):
        """Create a new note."""
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
        """Delete a note."""
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
        """Load a note for editing."""
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
        """Save current note."""
        note_error.value = ""
        current = notes_manager.get_current_note()
        if not current["success"]:
            note_error.value = "Select or create a note first."
            page.update()
            return

        # Update content
        result = notes_manager.update_note(
            notes_manager.current_note_index, note_editor.value
        )
        if not result["success"]:
            note_error.value = result["message"]
            page.update()
            return

        # Update language
        lang_result = notes_manager.set_note_language(
            notes_manager.current_note_index, note_lang.value
        )
        if not lang_result["success"]:
            note_error.value = lang_result["message"]
            page.update()
            return

        note_error.value = "Saved!"
        note_error.color = SUCCESS_COLOR
        page.update()

    def on_text_change(e):
        """Handle text change and update predictions."""
        lang = note_lang.value or "cz"
        preds = notes_manager.get_predictions(note_editor.value, lang)
        predictions_row.controls.clear()
        for p in preds:
            predictions_row.controls.append(
                ft.Chip(
                    label=ft.Text(p, size=12),
                    on_click=lambda e, word=p: insert_word(word),
                )
            )
        page.update()

    def insert_word(word):
        """Insert predicted word into editor."""
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

    note_actions_row = ft.Row(
        [note_lang, btn("Save", save_note_handler, primary=True)], visible=False
    )

    refresh_notes_list()

    # ── Assembly ────────────────────────────────────
    return ft.Column(
        [
            section("Notepad"),
            sub("Create/load a note to start writing with word prediction."),
            ft.Row([note_title_input, btn("New Note", create_note_handler)]),
            note_error,
            note_info,
            ft.Row(
                [
                    # Left: notes list
                    ft.Container(
                        content=ft.Column(
                            [
                                notes_list_header,
                                ft.Container(content=notes_list, expand=True),
                            ],
                            spacing=4,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        width=180,
                        alignment=ft.Alignment(0, -1),
                    ),
                    ft.VerticalDivider(),
                    # Right: editor with predictions
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        suggestions_label,
                                        predictions_row,
                                    ],
                                    spacing=4,
                                ),
                                height=60,
                            ),
                            ft.Container(
                                content=note_editor,
                                expand=True,
                                border=ft.Border.all(1, GREY_300_COLOR),
                                border_radius=4,
                            ),
                            note_actions_row,
                        ],
                        spacing=6,
                        expand=True,
                    ),
                ],
                expand=True,
            ),
        ],
        spacing=10,
    )
