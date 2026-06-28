import sqlite3
import os

DB_FILE = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.db"

def connect_db():
    if not os.path.exists(DB_FILE):
        print("❌ SQLite-Datenbank nicht gefunden:", DB_FILE)
        return None
    try:
        return sqlite3.connect(DB_FILE)
    except Exception as e:
        print("❌ Fehler beim Öffnen der DB:", e)
        return None


def get_plz_info(plz):
    conn = connect_db()
    if conn is None:
        return None

    cur = conn.cursor()
    row = cur.execute(
        "SELECT plz, bundesland, ort FROM plz WHERE plz = ?", (plz,)
    ).fetchone()

    conn.close()

    if row:
        return {
            "plz": row[0],
            "bundesland": row[1],
            "ort": row[2]
        }
    else:
        return None


def get_city_from_plz(plz):
    info = get_plz_info(plz)
    if info:
        return info["ort"]
    return "Unbekannte Stadt"


def get_bundesland_from_plz(plz):
    info = get_plz_info(plz)
    if info:
        return info["bundesland"]
    return "Unbekanntes Bundesland"
