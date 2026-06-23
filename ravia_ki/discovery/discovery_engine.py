from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import time
import re

# -----------------------------------------
# Hersteller-Profile
# -----------------------------------------

LG_PROFILE = {
    "name": "LG",
    "seeds": [
        "https://www.lg.com/global/business/air-solution",
        "https://www.lg.com/global/business/air-solution/air-to-water-heat-pump",
    ],
    "product_keywords": ["product", "air", "solution", "heat", "pump"],
    "scroll": True,
    "click_download_tab": True,
}

PANASONIC_PROFILE = {
    "name": "Panasonic",
    "seeds": [
        "https://www.panasonic.com/global/business/psna/air-conditioning.html",
    ],
    "product_keywords": ["product", "aquarea", "heat", "pump"],
    "scroll": True,
    "click_download_tab": True,
}

DAIKIN_PROFILE = {
    "name": "Daikin",
    "seeds": [
        "https://www.daikin.eu/en_us/products.html",
    ],
    "product_keywords": ["product", "heat", "pump", "altherma"],
    "scroll": False,
    "click_download_tab": False,
}

VAILLANT_PROFILE = {
    "name": "Vaillant",
    "seeds": [
        "https://www.vaillant.de/produkte/",
    ],
    "product_keywords": ["produkt", "produktdetail", "aro", "therm"],
    "scroll": False,
    "click_download_tab": True,
}

MANUFACTURERS = {
    "lg": LG_PROFILE,
    "panasonic": PANASONIC_PROFILE,
    "daikin": DAIKIN_PROFILE,
    "vaillant": VAILLANT_PROFILE,
}

# -----------------------------------------
# PDF-Klassifikation
# -----------------------------------------

CATEGORIES = {
    "fehlerliste": [
        r"error", r"fault", r"fehler", r"diagnostic", r"troubleshoot"
    ],
    "datenblatt": [
        r"datasheet", r"spec", r"technical", r"tds", r"data"
    ],
    "explosionszeichnung": [
        r"exploded", r"parts", r"spare", r"ersatzteil", r"component"
    ],
    "installationsanleitung": [
        r"installation", r"install", r"montage", r"setup"
    ],
    "bedienungsanleitung": [
        r"user", r"manual", r"bedien", r"operation", r"guide"
    ],
    "servicemanual": [
        r"service", r"repair", r"maintenance", r"wartung"
    ],
    "hydraulikschema": [
        r"hydraulic", r"schema", r"schematic", r"piping"
    ],
    "katalog": [
        r"catalog", r"brochure", r"marketing"
    ],
    "ersatzteile": [
        r"parts", r"spare", r"component"
    ],
}

def classify_pdf(url: str) -> str:
    u = url.lower()
    for category, patterns in CATEGORIES.items():
        for p in patterns:
            if re.search(p, u):
                return category
    return "unbekannt"


# -----------------------------------------
# Discovery Engine
# -----------------------------------------

class DiscoveryEngine:
    def __init__(self):
        pass

    def discover_manufacturer(self, manufacturer: str) -> dict:
        profile = MANUFACTURERS[manufacturer.lower()]
        return self._discover_with_profile(profile)

    def _discover_with_profile(self, profile: dict) -> dict:
        pdfs: list[dict] = []
        product_pages: list[str] = []

        print(f"[Discovery] Starte Browser für {profile['name']}...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            # -----------------------------
            # STUFE 1: Produktseiten sammeln
            # -----------------------------
            for seed in profile["seeds"]:
                print(f"[Discovery] Lade Seed: {seed}")

                try:
                    page = context.new_page()
                    page.goto(seed, timeout=30000, wait_until="networkidle")

                    links = page.locator("a[href]").all()
                    print(f"[Discovery] Gefundene Links auf Seed: {len(links)}")

                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue

                        full = urljoin(seed, href)
                        lower = full.lower()

                        if any(k in lower for k in profile["product_keywords"]):
                            product_pages.append(full)

                except Exception as e:
                    print(f"[Discovery] Fehler bei Seed {seed}: {e}")

            product_pages = list(dict.fromkeys(product_pages))
            print(f"[Discovery] Produktseiten gefunden: {len(product_pages)}")

            # -----------------------------
            # STUFE 2: PDFs extrahieren
            # -----------------------------
            for url in product_pages:
                print(f"[Discovery] Öffne Produktseite: {url}")

                try:
                    page = context.new_page()
                    page.goto(url, timeout=30000, wait_until="networkidle")

                    if profile.get("scroll", False):
                        page.mouse.wheel(0, 2000)
                        time.sleep(1)

                    if profile.get("click_download_tab", False):
                        for text in ["Download", "Downloads", "Manuals", "Documents"]:
                            try:
                                page.click(f"text={text}")
                                time.sleep(1)
                            except Exception:
                                continue

                    links = page.locator("a[href]").all()
                    print(f"[Discovery] Links auf Produktseite: {len(links)}")

                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue

                        full = urljoin(url, href)
                        lower = full.lower()

                        if ".pdf" in lower:
                            category = classify_pdf(full)
                            print(f"[Discovery] PDF gefunden: {full} [{category}]")
                            pdfs.append({"url": full, "category": category})

                except Exception as e:
                    print(f"[Discovery] Fehler bei Produktseite {url}: {e}")

            browser.close()

        return {
            "manufacturer": profile["name"],
            "pdfs": pdfs,
            "product_pages": product_pages,
        }
