"""Notepad with Czech/English word prediction — JSON persistence."""

import json
import os
import re


NOTES_PATH = os.path.join(os.path.dirname(__file__), "notes.json")

# Common Czech words for prediction
CZ_WORDS = [
    "ahoj", "jak", "se", "máš", "dobře", "díky", "prosím", "ano", "ne",
    "škola", "učitel", "žák", "třída", "předmět", "úkol", "zkouška",
    "počítač", "program", "síť", "internet", "web", "data", "soubor",
    "adresář", "složka", "text", "obrázek", "zvuk", "video",
    "matematika", "fyzika", "chemie", "biologie", "dějepis", "zeměpis",
    "informatika", "jazyk", "český", "anglický", "německý",
    "kalkulačka", "výpočet", "rovnice", "funkce", "graf", "tabulka",
    "poznámka", "zápis", "shrnutí", "přehled", "seznam", "plán",
    "dnes", "zítra", "včera", "pondělí", "úterý", "středa", "čtvrtek",
    "pátek", "sobota", "neděle", "ráno", "večer", "noc",
    "dobrý", "špatný", "velký", "malý", "nový", "starý",
    "jeden", "dva", "tři", "čtyři", "pět", "šest", "sedm",
    "být", "mít", "dělat", "jít", "chtít", "moci", "vědět",
    "tak", "že", "když", "proto", "nebo", "a", "ale", "protože",
    "tento", "tamten", "který", "co", "kde", "kdy", "proč", "jak",
    "systém", "nastavení", "konfigurace", "instalace", "aplikace",
    "server", "klient", "databáze", "heslo", "přístup", "správce",
    "projekt", "test", "kontrola", "výsledek", "chyba", "oprava",
]

# Common English words for prediction
EN_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "school", "computer", "program", "network", "data", "file", "folder",
    "system", "server", "client", "database", "password", "access",
    "project", "test", "result", "error", "fix", "code", "function",
    "class", "method", "variable", "value", "input", "output",
    "calculate", "equation", "graph", "table", "chart", "summary",
    "note", "write", "read", "learn", "study", "exam", "homework",
    "math", "physics", "chemistry", "biology", "history", "geography",
    "information", "technology", "language", "english", "german", "czech",
    "today", "tomorrow", "yesterday", "morning", "evening", "night",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "good", "bad", "big", "small", "new", "old", "first", "last",
    "one", "two", "three", "four", "five", "six", "seven",
    "is", "are", "was", "were", "has", "had", "can", "could",
    "should", "would", "may", "might", "must", "shall",
    "this", "that", "these", "those", "which", "who", "where", "when", "why", "how",
    "configuration", "installation", "application", "settings",
    "manager", "admin", "user", "group", "permission", "security",
]


def load_notes(path: str = NOTES_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_notes(notes: list[dict], path: str = NOTES_PATH) -> bool:
    try:
        with open(path, "w") as f:
            json.dump(notes, f, indent=2)
        return True
    except Exception:
        return False


def create_note(notes: list[dict], title: str) -> list[dict] | None:
    if not title.strip():
        return None
    notes.append({"title": title.strip(), "content": "", "created": True, "lang": "cz"})
    return notes


def update_note(notes: list[dict], index: int, content: str) -> list[dict] | None:
    if 0 <= index < len(notes):
        notes[index]["content"] = content
    return notes


def delete_note(notes: list[dict], index: int) -> list[dict] | None:
    if 0 <= index < len(notes):
        notes.pop(index)
    return notes


def set_note_lang(notes: list[dict], index: int, lang: str) -> list[dict] | None:
    if 0 <= index < len(notes):
        notes[index]["lang"] = lang
    return notes


def get_predictions(text: str, lang: str = "cz", max_suggestions: int = 5) -> list[str]:
    """Predict next words based on the last word typed."""
    words = re.findall(r'[a-zA-ZáčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]+', text)
    if not words:
        return []

    last_word = words[-1].lower()
    word_list = CZ_WORDS if lang == "cz" else EN_WORDS

    # Find words that start with the last word (prefix match)
    suggestions = [w for w in word_list if w.startswith(last_word) and w != last_word]
    # If no prefix match, suggest common words
    if not suggestions:
        suggestions = word_list[:max_suggestions]
    else:
        # Sort by length (shorter first) and deduplicate
        suggestions = sorted(set(suggestions), key=lambda w: (len(w), w))

    return suggestions[:max_suggestions]

