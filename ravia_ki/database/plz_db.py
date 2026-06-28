import sqlite3
import os

# Absoluter Pfad zur korrekten Datenbank
DB_FILE = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.db"


def connect_db():
    """Stellt eine Verbindung zur SQLite-Datenbank her."""
    if not os.path.exists(DB_FILE):
        print("❌ SQLite-Datenbank nicht gefunden:", DB_FILE)
        return None

    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except Exception as e:
        print("❌ Fehler beim Öffnen der DB:", e)
        return None


def get_plz_info(plz):
    """Liest PLZ-Daten aus der SQLite-Datenbank."""
    conn = connect_db()
    if conn is None:
        return None

    try:
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

    except sqlite3.OperationalError as e:
        print("❌ SQL-Fehler:", e)
        print("⚠️ Tabelle 'plz' existiert nicht in:", DB_FILE)
        conn.close()
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
def update_city(plz, new_city):
    """Aktualisiert den Ort einer PLZ in der SQLite-Datenbank."""
    conn = connect_db()
    if conn is None:
        return False

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE plz SET ort = ? WHERE plz = ?",
            (new_city, plz)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Fehler beim Aktualisieren:", e)
        conn.close()
        return False
