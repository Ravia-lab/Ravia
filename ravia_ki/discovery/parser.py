import logging
from pathlib import Path
from typing import Optional

import chardet

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class Parser:
    def __init__(self, max_chars: int = 500_000):
        self.max_chars = max_chars

    def parse(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()

        try:
            if suffix == ".pdf":
                return self._parse_pdf(file_path)
            elif suffix in {".html", ".htm"}:
                return self._parse_html(file_path)
            elif suffix in {".txt", ""}:
                return self._parse_text(file_path)
            else:
                # Fallback: erst Text, dann ggf. HTML-Heuristik
                text = self._parse_text(file_path)
                if text.strip():
                    return text
                return self._parse_html(file_path)
        except Exception as e:
            logging.error(f"[Parser] Fehler beim Parsen von {file_path}: {e}")
            return ""

    def _parse_pdf(self, file_path: Path) -> str:
        if pdfplumber is None:
            logging.error("[Parser] pdfplumber nicht installiert")
            return ""

        text_chunks = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_chunks.append(page_text)
                if sum(len(t) for t in text_chunks) > self.max_chars:
                    break

        text = "\n".join(text_chunks)
        return text[: self.max_chars]

    def _detect_encoding(self, data: bytes) -> Optional[str]:
        try:
            result = chardet.detect(data)
            enc = result.get("encoding")
            return enc or "utf-8"
        except Exception:
            return "utf-8"

    def _parse_text(self, file_path: Path) -> str:
        raw = file_path.read_bytes()
        encoding = self._detect_encoding(raw)
        try:
            text = raw.decode(encoding, errors="replace")
        except Exception:
            text = raw.decode("utf-8", errors="replace")
        return text[: self.max_chars]

    def _parse_html(self, file_path: Path) -> str:
        if BeautifulSoup is None:
            logging.error("[Parser] BeautifulSoup (bs4) nicht installiert")
            return ""

        raw = file_path.read_bytes()
        encoding = self._detect_encoding(raw)
        try:
            html = raw.decode(encoding, errors="replace")
        except Exception:
            html = raw.decode("utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")

        # Skripte/Styles entfernen
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        # Whitespace normalisieren
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)

        return text[: self.max_chars]
