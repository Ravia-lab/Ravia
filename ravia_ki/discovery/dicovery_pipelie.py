import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import fitz  # PyMuPDF
import sqlite3


# ============================================================
# 1. Websuche (Bing-ähnlich)
# ============================================================
class WebSearchCollector:

    def search(self, query):
        q = quote(f"{query} filetype:pdf")
        url = f"https://www.bing.com/search?q={q}"

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            results = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith(".pdf"):
                    results.append(href)

            return list(set(results))

        except Exception:
            return []


# ============================================================
# 2. PDF-Extraktion von HTML-Seiten
# ============================================================
class PDFLinkExtractor:

    def extract(self, url):
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            pdfs = []
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if href.endswith(".pdf"):
                    pdfs.append(urljoin(url, href))

            return list(set(pdfs))

        except Exception:
            return []


# ============================================================
# 3. Deep Scanner (folgt Links, scannt tiefer)
# ============================================================
class DeepPDFScanner:

    def deep_scan(self, url, depth=2, visited=None):
        if visited is None:
            visited = set()

        if depth == 0 or url in visited:
            return []

        visited.add(url)

        extractor = PDFLinkExtractor()
        pdfs = extractor.extract(url)

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a", href=True):
                next_url = urljoin(url, a["href"])
                pdfs.extend(self.deep_scan(next_url, depth - 1, visited))

        except Exception:
            pass

        return list(set(pdfs))


# ============================================================
# 4. Händlerseiten (öffentlich, viele PDFs)
# ============================================================
class DealerSiteScanner:

    DEALERS = [
        "https://www.heizungsfinder.de",
        "https://www.klimaworld.com",
        "https://www.energieheld.de",
        "https://www.klimageraete.de",
    ]

    def scan_all(self):
        extractor = PDFLinkExtractor()
        results = []

        for site in self.DEALERS:
            results.extend(extractor.extract(site))

        return list(set(results))


# ============================================================
# 5. Foren (öffentliche PDF-Links)
# ============================================================
class ForumPDFHunter:

    FORUMS = [
        "https://www.haustechnikdialog.de",
        "https://www.waermepumpen-forum.de",
        "https://www.energiesparhaus.at",
        "https://www.reddit.com/r/heatpumps",
    ]

    def scan(self):
        extractor = PDFLinkExtractor()
        results = []

        for forum in self.FORUMS:
            results.extend(extractor.extract(forum))

        return list(set(results))


# ============================================================
# 6. PDF-Klassifikation
# ============================================================
class PDFClassifier:

    KEYWORDS = {
        "installationsanleitung": [
            "installation", "installationsanleitung", "montage",
            "installation manual", "installation guide",
            "montageanleitung", "anschluss", "aufstellung"
        ],
        "servicemanual": [
            "service manual", "wartung", "maintenance",
            "troubleshooting", "repair", "diagnose",
            "fehlersuche", "service information"
        ],
        "hydraulikplan": [
            "hydraulic", "hydraulik", "piping", "schema",
            "schematic", "anschlussplan", "rohrschema"
        ],
        "datenblatt": [
            "datasheet", "technical data", "specification",
            "leistungsdaten", "produktdaten", "technische daten"
        ],
        "ersatzteile": [
            "spare parts", "ersatzteile", "parts list",
            "exploded view", "component list"
        ],
        "fehlerliste": [
            "error code", "error list", "fehlermeldung",
            "error table", "error description"
        ],
        "planungsunterlage": [
            "planning", "planungsunterlage", "design guide",
            "dimensioning", "sizing", "auslegung"
        ],
        "schulung": [
            "training", "schulung", "seminar", "education",
            "training material", "training manual"
        ],
    }

    def extract_text(self, pdf_path, max_pages=3):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for i in range(min(max_pages, len(doc))):
                text += doc[i].get_text()
            return text.lower()
        except Exception:
            return ""

    def classify(self, pdf_path):
        filename = pdf_path.lower()
        text = self.extract_text(pdf_path)

        scores = {cat: 0 for cat in self.KEYWORDS}

        for category, words in self.KEYWORDS.items():
            for w in words:
                if w in filename:
                    scores[category] += 3
                if w in text:
                    scores[category] += 1

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "unbekannt"


# ============================================================
# 7. PDF-Downloader
# ============================================================
class PDFDownloader:

    def download(self, url, folder="downloads"):
        os.makedirs(folder, exist_ok=True)

        filename = url.split("/")[-1]
        path = os.path.join(folder, filename)

        try:
            r = requests.get(url, timeout=15)
            with open(path, "wb") as f:
                f.write(r.content)
            return path
        except Exception:
            return None


# ============================================================
# 8. SQLite-Datenbank
# ============================================================
class PDFDatabase:

    def __init__(self, db_path="ravia_discovery.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT,
                url TEXT,
                local_path TEXT,
                category TEXT
            )
        """)

    def insert(self, product, url, path, category):
        self.conn.execute(
            "INSERT INTO pdfs (product, url, local_path, category) VALUES (?, ?, ?, ?)",
            (product, url, path, category)
        )
        self.conn.commit()


# ============================================================
# 9. MASTER-PIPELINE
# ============================================================
class DiscoveryPipeline:

    def __init__(self):
        self.web = WebSearchCollector()
        self.dealer = DealerSiteScanner()
        self.forums = ForumPDFHunter()
        self.deep = DeepPDFScanner()
        self.downloader = PDFDownloader()
        self.classifier = PDFClassifier()
        self.db = PDFDatabase()

    def run(self, product_name):
        print(f"🔍 Suche PDFs für: {product_name}")

        results = []

        # 1. Websuche
        results.extend(self.web.search(product_name))

        # 2. Händlerseiten
        results.extend(self.dealer.scan_all())

        # 3. Foren
        results.extend(self.forums.scan())

        # 4. Deep Scan (Top 10)
        for url in results[:10]:
            results.extend(self.deep.deep_scan(url))

        results = list(set(results))

        print(f"📄 Gefundene PDF-Links: {len(results)}")

        # 5. Download + Klassifikation + DB
        for url in results:
            path = self.downloader.download(url)
            if not path:
                continue

            category = self.classifier.classify(path)
            self.db.insert(product_name, url, path, category)

            print(f"✔ {category.upper()} → {path}")


# ============================================================
# 10. Beispiel
# ============================================================
if __name__ == "__main__":
    pipeline = DiscoveryPipeline()
    pipeline.run("LG Therma V R290 Monobloc")
