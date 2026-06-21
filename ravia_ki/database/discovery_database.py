import sqlite3
from datetime import datetime
from urllib.parse import urlparse


class DiscoveryDatabase:
    def __init__(self, db_path="ravia_discovery.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS discovery_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            manufacturer TEXT,
            model TEXT,
            kw TEXT,
            url TEXT,
            type TEXT,
            domain TEXT,
            source TEXT,
            status TEXT
        )
        """)

        conn.commit()
        conn.close()

    def insert_result(self, manufacturer, model, kw, url, type, source, status="valid"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        domain = urlparse(url).netloc
        timestamp = datetime.now().isoformat()

        c.execute("""
        INSERT INTO discovery_results 
        (timestamp, manufacturer, model, kw, url, type, domain, source, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, manufacturer, model, kw, url, type, domain, source, status))

        conn.commit()
        conn.close()

    def get_all(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM discovery_results")
        rows = c.fetchall()
        conn.close()
        return rows

    def get_by_device(self, manufacturer, model, kw):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        SELECT * FROM discovery_results
        WHERE manufacturer=? AND model=? AND kw=?
        """, (manufacturer, model, kw))
        rows = c.fetchall()
        conn.close()
        return rows
