import json
import os

ROOMS_FILE = "rooms.json"


def load_rooms():
    """Lädt Räume aus rooms.json."""
    if not os.path.exists(ROOMS_FILE):
        return []
    try:
        with open(ROOMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_rooms(rooms):
    """Speichert Räume in rooms.json."""
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(rooms, f, indent=4, ensure_ascii=False)
