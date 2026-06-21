import requests
from pathlib import Path
from bs4 import BeautifulSoup


class Downloader:
    def __init__(self, base_dir="downloads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        }

    def download(self, url: str) -> Path | None:
        file_name = url.split("/")[-1].split("?")[0] or "downloaded_file"
        file_path = self.base_dir / file_name

        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()

            # Prüfen: Ist es ein echtes PDF?
            if response.content.startswith(b"%PDF"):
                file_path.write_bytes(response.content)
                print(f"[Downloader] ECHTES PDF geladen: {url}")
                return file_path

            # Wenn kein PDF → HTML-Wrapper
            print("[Downloader] HTML-Wrapper erkannt → extrahiere echten PDF-Link...")

            soup = BeautifulSoup(response.text, "html.parser")
            pdf_link = None

            # Suche nach echten PDF-Links
            for a in soup.find_all("a", href=True):
                if ".pdf" in a["href"].lower():
                    pdf_link = a["href"]
                    break

            if not pdf_link:
                print("[Downloader] Kein PDF-Link im HTML gefunden")
                return None

            # Absoluten Link bauen
            if pdf_link.startswith("/"):
                from urllib.parse import urljoin
                pdf_link = urljoin(url, pdf_link)

            print(f"[Downloader] Gefundener PDF-Link: {pdf_link}")

            # ECHTES PDF herunterladen
            pdf_response = requests.get(pdf_link, headers=self.headers, timeout=20)
            pdf_response.raise_for_status()

            if not pdf_response.content.startswith(b"%PDF"):
                print("[Downloader] Gefundene Datei ist trotzdem kein PDF")
                return None

            file_path.write_bytes(pdf_response.content)
            print(f"[Downloader] ECHTES PDF erfolgreich geladen: {pdf_link}")
            return file_path

        except Exception as e:
            print(f"[Downloader] Fehler bei {url}: {e}")
            return None
