"""Flashcard study system — library functions with JSON persistence and timestamps."""

import json
import os
import random
import time
from pathlib import Path


# Use app data folder instead of managers directory
DATA_DIR = Path.home() / ".ittoolbox" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_PATH = DATA_DIR / "flashcards.json"


def load_decks(path: str = DEFAULT_PATH) -> dict:
    """Load all decks from JSON file. Returns dict of deck_name -> list of cards.

    Decks are sorted by most recent first (by modified_time).
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            decks = json.load(f)
            # Sort decks by modified_time (most recent first)
            if isinstance(decks, dict):
                return dict(sorted(decks.items(),
                                   key=lambda x: x[1].get("modified_time", 0) if isinstance(x[1], dict) else 0,
                                   reverse=True))
            return {}
    except Exception:
        return {}


def save_decks(decks: dict, path: str = DEFAULT_PATH) -> bool:
    try:
        with open(path, "w") as f:
            json.dump(decks, f, indent=2)
        return True
    except Exception:
        return False


def create_deck(decks: dict, name: str) -> dict | None:
    if name.strip() in decks:
        return None
    now = time.time()
    decks[name.strip()] = {
        "cards": [],
        "created_time": now,
        "modified_time": now
    }
    return decks


def delete_deck(decks: dict, name: str) -> dict:
    decks.pop(name, None)
    return decks


def add_card(decks: dict, deck_name: str, front: str, back: str) -> dict | None:
    if deck_name not in decks:
        return None

    # Handle both old format (list) and new format (dict with metadata)
    if isinstance(decks[deck_name], list):
        # Migrate old format
        decks[deck_name] = {
            "cards": decks[deck_name],
            "created_time": time.time(),
            "modified_time": time.time()
        }

    decks[deck_name]["cards"].append({"front": front, "back": back, "added_time": time.time()})
    decks[deck_name]["modified_time"] = time.time()
    return decks


def delete_card(decks: dict, deck_name: str, index: int) -> dict | None:
    if deck_name not in decks:
        return None

    cards = decks[deck_name].get("cards") if isinstance(decks[deck_name], dict) else decks[deck_name]
    if 0 <= index < len(cards):
        cards.pop(index)
        if isinstance(decks[deck_name], dict):
            decks[deck_name]["modified_time"] = time.time()
    return decks


def start_quiz(decks: dict, deck_name: str) -> list[dict] | None:
    """Shuffle cards for quiz mode."""
    if deck_name not in decks:
        return None

    cards = decks[deck_name].get("cards") if isinstance(decks[deck_name], dict) else decks[deck_name]
    if not cards:
        return None

    shuffled = cards[:]
    random.shuffle(shuffled)
    return shuffled


class FlashcardManager:
    """Flashcard system manager with deck and card operations."""

    def __init__(self, path: str = DEFAULT_PATH):
        self.path = path
        self.decks = load_decks(path)
        self.current_deck = None
        self.quiz_cards = []
        self.quiz_index = 0
        self.show_back = False

    def save(self) -> bool:
        """Save decks to file."""
        return save_decks(self.decks, self.path)

    def create_deck(self, name: str) -> dict:
        """Create a new deck."""
        result = create_deck(self.decks, name)
        if result is None:
            return {"success": False, "message": "Deck already exists."}
        self.save()
        return {"success": True, "message": f"Deck '{name}' created."}

    def delete_deck(self, name: str) -> dict:
        """Delete a deck."""
        if name not in self.decks:
            return {"success": False, "message": "Deck not found."}
        delete_deck(self.decks, name)
        self.save()
        if self.current_deck == name:
            self.current_deck = None
        return {"success": True, "message": f"Deck '{name}' deleted."}

    def add_card(self, deck_name: str, front: str, back: str) -> dict:
        """Add a card to a deck."""
        result = add_card(self.decks, deck_name, front, back)
        if result is None:
            return {"success": False, "message": "Deck not found."}
        self.save()
        return {"success": True, "message": "Card added."}

    def delete_card(self, deck_name: str, index: int) -> dict:
        """Delete a card from a deck."""
        result = delete_card(self.decks, deck_name, index)
        if result is None:
            return {"success": False, "message": "Deck or card not found."}
        self.save()
        return {"success": True, "message": "Card deleted."}

    def get_deck_names(self) -> list:
        """Get list of deck names."""
        return list(self.decks.keys())

    def get_deck_info(self, name: str) -> dict:
        """Get information about a deck."""
        if name not in self.decks:
            return {"success": False, "message": "Deck not found."}

        deck = self.decks[name]
        # Handle both old format (list) and new format (dict with metadata)
        if isinstance(deck, dict) and "cards" in deck:
            return {
                "success": True,
                "name": name,
                "card_count": len(deck["cards"]),
                "cards": deck["cards"],
                "created_time": deck.get("created_time"),
                "modified_time": deck.get("modified_time")
            }
        else:
            # Old format
            return {
                "success": True,
                "name": name,
                "card_count": len(deck) if isinstance(deck, list) else 0,
                "cards": deck if isinstance(deck, list) else []
            }

    def start_quiz(self, deck_name: str) -> dict:
        """Start a quiz for a deck."""
        cards = start_quiz(self.decks, deck_name)
        if cards is None:
            return {"success": False, "message": "Deck not found or empty."}
        self.current_deck = deck_name
        self.quiz_cards = cards
        self.quiz_index = 0
        self.show_back = False
        return {"success": True, "message": f"Quiz started with {len(cards)} cards."}

    def get_current_card(self) -> dict:
        """Get the current quiz card."""
        if not self.quiz_cards or self.quiz_index >= len(self.quiz_cards):
            return {"success": False, "message": "No active quiz."}
        card = self.quiz_cards[self.quiz_index]
        return {
            "success": True,
            "front": card["front"],
            "back": card["back"] if self.show_back else None,
            "index": self.quiz_index + 1,
            "total": len(self.quiz_cards)
        }

    def flip_card(self) -> dict:
        """Flip the current card to show back."""
        if not self.quiz_cards or self.quiz_index >= len(self.quiz_cards):
            return {"success": False, "message": "No active quiz."}
        self.show_back = True
        return self.get_current_card()

    def next_card(self) -> dict:
        """Move to next card in quiz."""
        if not self.quiz_cards:
            return {"success": False, "message": "No active quiz."}
        self.quiz_index += 1
        self.show_back = False
        if self.quiz_index >= len(self.quiz_cards):
            return {"success": False, "message": "Quiz completed."}
        return self.get_current_card()

    def restart_quiz(self) -> dict:
        """Restart the current quiz."""
        if not self.current_deck:
            return {"success": False, "message": "No active quiz."}
        return self.start_quiz(self.current_deck)
