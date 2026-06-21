from ravia_ki.discovery.downloader import Downloader
from ravia_ki.discovery.parser import Parser
from ravia_ki.database.unified_db import UnifiedProductDatabase


class Pipeline:
    def __init__(self):
        self.db = UnifiedProductDatabase()
        self.downloader = Downloader()
        self.parser = Parser()

    def process_url(self, url: str):
        print(f"[Pipeline] Verarbeite: {url}")

        # 1. Download
        file_path = self.downloader.download(url)
        if not file_path:
            self.db.save_document(url, "unknown", "N/A", status="failed")
            return

        # PDF‑Fake‑Check (HTML‑Wrapper)
        if file_path.suffix.lower() == ".pdf":
            if not file_path.read_bytes().startswith(b"%PDF"):
                print("[Pipeline] WARNUNG: Datei ist kein echtes PDF → HTML‑Wrapper erkannt")
                self.db.save_document(url, "html-wrapper", file_path, status="failed")
                return

        suffix = file_path.suffix.lower()
        file_type = suffix.lstrip(".") or "unknown"

        # 2. Dokument speichern
        doc_id = self.db.save_document(url, file_type, file_path)

        # 3. Parser
        text = self.parser.parse(file_path)

        if text.strip():
            self.db.save_raw_text(doc_id, text)
            print(f"[Pipeline] Text extrahiert ({len(text)} Zeichen)")
        else:
            print("[Pipeline] Kein Text extrahiert")

    def process_urls(self, urls: list[str]):
        for url in urls:
            self.process_url(url)
