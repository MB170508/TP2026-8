"""Flashcard study system — library functions with JSON persistence."""

import json
import os
import random


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "flashcards.json")


def load_decks(path: str = DEFAULT_PATH) -> dict:
    """Load all decks from JSON file. Returns dict of deck_name -> list of cards."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


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
    decks[name.strip()] = []
    return decks


def delete_deck(decks: dict, name: str) -> dict:
    decks.pop(name, None)
    return decks


def add_card(decks: dict, deck_name: str, front: str, back: str) -> dict | None:
    if deck_name not in decks:
        return None
    decks[deck_name].append({"front": front, "back": back})
    return decks


def delete_card(decks: dict, deck_name: str, index: int) -> dict | None:
    if deck_name not in decks:
        return None
    if 0 <= index < len(decks[deck_name]):
        decks[deck_name].pop(index)
    return decks


def start_quiz(decks: dict, deck_name: str) -> list[dict] | None:
    """Shuffle cards for quiz mode."""
    if deck_name not in decks or not decks[deck_name]:
        return None
    cards = decks[deck_name][:]
    random.shuffle(cards)
    return cards
