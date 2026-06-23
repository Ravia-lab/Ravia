import logging
import mimetypes
from pathlib import Path
from ravia_ki.discovery.downloader import Downloader
from ravia_ki.discovery.parser import Parser
from ravia_ki.database.unified_db import UnifiedProductDatabase


class Pipeline:
    def __init__(self, retries: int = 2):
        self.db = UnifiedProductDatabase()
        self.downloader = Downloader()
        self.parser = Parser()
        self.retries = retries

    def _detect_mime(self, file_path: Path) -> str:
        mime, _ = mimetypes.guess_type(str(file_path))
        return mime or "application/octet-stream"

    def _is_real_pdf(self, file_path: Path) -> bool:
        try:
            return file_path.read_bytes().startswith(b"%PDF")
        except Exception:
            return False

    def _download_with_retry(self, url: str):
        for attempt in range(1, self.retries + 1):
            try:
                file_path = self.downloader.download(url)
                if file_path:
                    return file_path
            except Exception as e:
                logging.error(f"[Pipeline] Download-Fehler (Versuch {attempt}): {e}")
        return None

    def process_url(self, url: str) -> dict:
        logging.info(f"[Pipeline] Verarbeite: {url}")

        # Duplicate Check
        if self.db.document_exists(url):
            return {"url": url, "status": "duplicate"}

        # Download
        file_path = self._download_with_retry(url)
        if not file_path:
            self.db.save_document(url, "unknown", "N/A", status="download_failed")
            return {"url": url, "status": "download_failed"}

        mime = self._detect_mime(file_path)
        suffix = file_path.suffix.lower().lstrip(".") or "unknown"

        # PDF Fake Check
        if suffix == "pdf" and not self._is_real_pdf(file_path):
            self.db.save_document(url, "html-wrapper", file_path, status="html_wrapper")
            return {"url": url, "status": "html_wrapper"}

        # Save Document
        doc_id = self.db.save_document(url, suffix, file_path, mime=mime)

        # Parse
        try:
            text = self.parser.parse(file_path)
        except Exception as e:
            logging.error(f"[Pipeline] Parser-Fehler: {e}")
            return {"url": url, "status": "parse_error"}

        if text.strip():
            self.db.save_raw_text(doc_id, text)
            return {
                "url": url,
                "status": "ok",
                "chars": len(text),
                "doc_id": doc_id,
                "mime": mime
            }

        return {"url": url, "status": "empty", "doc_id": doc_id, "mime": mime}

    def process_urls(self, urls: list[str]) -> list[dict]:
        results = []
        for url in urls:
            results.append(self.process_url(url))
        return results
