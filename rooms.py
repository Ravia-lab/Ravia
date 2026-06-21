import json
import os

ROOMS_FILE = "rooms.json"


def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return []
    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_rooms(rooms):
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(rooms, f, indent=4, ensure_ascii=False)


def add_room(room: dict):
    rooms = load_rooms()
    rooms.append(room)
    save_rooms(rooms)


def delete_room(name: str):
    rooms = load_rooms()
    rooms = [r for r in rooms if r.get("name") != name]
    save_rooms(rooms)


def update_room(old_name: str, new_room: dict):
    rooms = load_rooms()
    for i, r in enumerate(rooms):
        if r.get("name") == old_name:
            rooms[i] = new_room
            break
    save_rooms(rooms)
