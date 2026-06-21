from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
from .filters import is_relevant_domain, is_probably_pdf
from .url_utils import normalize_url


class DiscoveryEngine:
    def __init__(self):
        pass

    def discover(self, seed_urls: list[str]) -> dict:
        pdfs = []
        htmls = []

        print("[Discovery] Starte Browser...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for seed in seed_urls:
                print(f"[Discovery] Lade: {seed}")

                try:
                    page = context.new_page()
                    page.goto(seed, timeout=30000, wait_until="networkidle")

                    links = page.locator("a[href]").all()
                    print(f"[Discovery] Gefundene Links: {len(links)}")

                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue

                        full = normalize_url(seed, href)

                        if is_probably_pdf(full):
                            print(f"[Discovery] PDF gefunden: {full}")
                            pdfs.append(full)
                        elif is_relevant_domain(full):
                            htmls.append(full)

                except Exception as e:
                    print(f"[Discovery] Fehler bei {seed}: {e}")

            browser.close()

        print("[Discovery] Fertig.")

        return {
            "pdfs": list(dict.fromkeys(pdfs)),
            "html": list(dict.fromkeys(htmls)),
        }
