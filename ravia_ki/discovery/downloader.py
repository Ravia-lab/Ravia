import logging
import requests
from pathlib import Path
from urllib.parse import urlparse
from time import sleep


class Downloader:
    def __init__(self, base_dir="downloads", retries=2, timeout=20):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.retries = retries
        self.timeout = timeout

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }

    def _safe_filename(self, url: str) -> str:
        parsed = urlparse(url)
        name = Path(parsed.path).name or "downloaded_file"
        return name.replace("/", "_").replace("\\", "_")

    def _download_once(self, url: str) -> Path | None:
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()

            file_name = self._safe_filename(url)
            file_path = self.base_dir / file_name
            file_path.write_bytes(response.content)

            return file_path

        except Exception as e:
            logging.error(f"[Downloader] Fehler bei {url}: {e}")
            return None

    def download(self, url: str) -> Path | None:
        for attempt in range(1, self.retries + 1):
            file_path = self._download_once(url)
            if file_path:
                logging.info(f"[Downloader] OK: {url}")
                return file_path

            logging.warning(f"[Downloader] Retry {attempt}/{self.retries} für {url}")
            sleep(1.0 * attempt)

        logging.error(f"[Downloader] Abbruch nach {self.retries} Versuchen: {url}")
        return None
