import pdfplumber
from bs4 import BeautifulSoup
from pathlib import Path
import zipfile


class Parser:
    def parse(self, file_path: Path) -> str:
        """
        Erkennt automatisch den Dateityp und extrahiert Text.
        """
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._parse_pdf(file_path)

        if suffix in [".html", ".htm"]:
            return self._parse_html(file_path)

        if suffix == ".zip":
            return self._parse_zip(file_path)

        return ""  # Bilder etc. ignorieren wir erstmal

    # -------------------------
    # PDF
    # -------------------------
    def _parse_pdf(self, file_path: Path) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
        except Exception as e:
            print(f"[Parser] PDF Fehler: {file_path} -> {e}")
        return text

    # -------------------------
    # HTML
    # -------------------------
    def _parse_html(self, file_path: Path) -> str:
        try:
            html = file_path.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n")
        except Exception as e:
            print(f"[Parser] HTML Fehler: {file_path} -> {e}")
            return ""

    # -------------------------
    # ZIP
    # -------------------------
    def _parse_zip(self, file_path: Path) -> str:
        text = ""
        try:
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                extract_dir = file_path.parent / (file_path.stem + "_unzipped")
                extract_dir.mkdir(exist_ok=True)
                zip_ref.extractall(extract_dir)

                for inner_file in extract_dir.rglob("*"):
                    if inner_file.suffix.lower() == ".pdf":
                        text += self._parse_pdf(inner_file)
                    elif inner_file.suffix.lower() in [".html", ".htm"]:
                        text += self._parse_html(inner_file)
        except Exception as e:
            print(f"[Parser] ZIP Fehler: {file_path} -> {e}")
        return text
