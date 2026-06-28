import sqlite3
import os
import pandas as pd

# Erst die Variablen definieren
XLS = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.xls"
DB  = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.db"

# Dann debuggen
print("DEBUG CWD:", os.getcwd())
print("DEBUG XLS:", XLS)
print("DEBUG DB:", DB)




def load_any_excel(path):
    """
    Versucht alle möglichen Formate:
    - XLS (BIFF)
    - XLSX
    - HTML disguised as XLS
    - CSV disguised as XLS
    """
    # 1) Versuch: klassisches Excel
    try:
        return pd.read_excel(path, header=None)
    except Exception as e:
        print("read_excel fehlgeschlagen:", e)

    # 2) Versuch: HTML
    try:
        return pd.read_html(path)[0]
    except Exception as e:
        print("read_html fehlgeschlagen:", e)

    # 3) Versuch: CSV
    try:
        return pd.read_csv(path, header=None, sep=None, engine="python")
    except Exception as e:
        print("read_csv fehlgeschlagen:", e)

    return None


def build_db(xls_file: str, db_file: str):
    # Alte DB löschen
    if os.path.exists(db_file):
        os.remove(db_file)

    df = load_any_excel(xls_file)

    if df is None:
        print("❌ Datei konnte nicht eingelesen werden.")
        return

    print("✔ Datei erfolgreich eingelesen")
    print(df.head())

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS plz (
        plz TEXT PRIMARY KEY,
        bundesland TEXT,
        ort TEXT
    );
    """)

    rows = []

    for _, row in df.iterrows():
        try:
            bundesland = str(row[0]).strip()
            plz = str(row[1]).strip()
            ort = str(row[2]).strip()
        except:
            continue

        if plz.isdigit() and len(plz) == 5:
            rows.append((plz, bundesland, ort))

    cur.executemany(
        "INSERT OR REPLACE INTO plz (plz, bundesland, ort) VALUES (?, ?, ?)",
        rows
    )

    conn.commit()
    conn.close()

    print(f"✔ Datenbank erstellt mit {len(rows)} Einträgen.")


if __name__ == "__main__":
    build_db(XLS, DB)
