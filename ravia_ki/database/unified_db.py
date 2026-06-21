import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List


DB_PATH = "ravia.db"


class UnifiedProductDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            file_type TEXT NOT NULL,
            local_path TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS raw_text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            text_content TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS product_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT,
            model TEXT,
            variant TEXT,
            power_kw REAL,
            cop REAL,
            scop REAL,
            noise_db REAL,
            refrigerant TEXT,
            voltage TEXT,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.commit()

    # -------------------------
    # Dokumente & Rohtext
    # -------------------------

    def save_document(self, url: str, file_type: str, local_path: Path, status: str = "downloaded") -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO documents (url, file_type, local_path, status)
            VALUES (?, ?, ?, ?)
        """, (url, file_type, str(local_path), status))
        self.conn.commit()
        return cur.lastrowid

    def save_raw_text(self, document_id: int, text: str) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO raw_text (document_id, text_content)
            VALUES (?, ?)
        """, (document_id, text))
        self.conn.commit()
        return cur.lastrowid

    # -------------------------
    # Extrahierte Daten
    # -------------------------

    def save_extracted_data(self, document_id: int, key: str, value: str, confidence: float = 0.8) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO extracted_data (document_id, key, value, confidence)
            VALUES (?, ?, ?, ?)
        """, (document_id, key, value, confidence))
        self.conn.commit()
        return cur.lastrowid

    def get_extracted_for_model_hint(self, model_hint: str) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT ed.key, ed.value, ed.confidence
            FROM extracted_data ed
            JOIN raw_text rt ON ed.document_id = rt.document_id
            WHERE rt.text_content LIKE ?
        """, (f"%{model_hint}%",))
        rows = cur.fetchall()
        return [
            {"key": r[0], "value": r[1], "confidence": r[2]}
            for r in rows
        ]

    # -------------------------
    # Merger: aus vielen Daten → ein Produkt
    # -------------------------

    def merge_to_product_master(self, manufacturer: str, model: str, variant_hint: Optional[str] = None):
        # Alle extrahierten Daten holen, die zum Modell passen
        extracted = self.get_extracted_for_model_hint(model)

        merged: Dict[str, Dict[str, Any]] = {}
        for item in extracted:
            key = item["key"]
            value = item["value"]
            conf = item["confidence"]

            if key not in merged or conf > merged[key]["confidence"]:
                merged[key] = {"value": value, "confidence": conf}

        def _get_float(k: str) -> Optional[float]:
            if k in merged:
                try:
                    return float(str(merged[k]["value"]).replace(",", "."))
                except ValueError:
                    return None
            return None

        def _get_str(k: str) -> Optional[str]:
            return str(merged[k]["value"]) if k in merged else None

        power_kw = _get_float("power_kw")
        cop = _get_float("cop")
        scop = _get_float("scop")
        noise_db = _get_float("noise_db")
        refrigerant = _get_str("refrigerant")
        voltage = _get_str("voltage")
        variant = variant_hint or _get_str("variant")

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO product_master (
                manufacturer, model, variant,
                power_kw, cop, scop, noise_db,
                refrigerant, voltage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            manufacturer, model, variant,
            power_kw, cop, scop, noise_db,
            refrigerant, voltage
        ))
        self.conn.commit()
        return cur.lastrowid

    # -------------------------
    # Produkt abfragen
    # -------------------------

    def get_product(self, manufacturer: str, model: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, manufacturer, model, variant,
                   power_kw, cop, scop, noise_db,
                   refrigerant, voltage, last_update
            FROM product_master
            WHERE manufacturer = ? AND model = ?
            ORDER BY last_update DESC
            LIMIT 1
        """, (manufacturer, model))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "manufacturer": row[1],
            "model": row[2],
            "variant": row[3],
            "power_kw": row[4],
            "cop": row[5],
            "scop": row[6],
            "noise_db": row[7],
            "refrigerant": row[8],
            "voltage": row[9],
            "last_update": row[10],
        }

    def close(self):
        self.conn.close()
