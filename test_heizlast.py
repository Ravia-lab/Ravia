import sqlite3

conn = sqlite3.connect("plz.db")
cur = conn.cursor()

row = cur.execute("SELECT * FROM plz LIMIT 5").fetchall()
print(row)
