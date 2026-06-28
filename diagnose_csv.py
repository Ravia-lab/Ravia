import sqlite3

DB = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

print("Tabellen:", cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())

print("\nErste 10 Zeilen:")
print(cur.execute("SELECT * FROM plz LIMIT 10").fetchall())

conn.close()
