import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote


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
# 6. MASTER-ENGINE: ULTIMATIVER PDF FINDER
# ============================================================
class UltimatePDFFinder:

    def find(self, product_name):
        results = []

        # 1. Websuche
        print("🔍 Websuche…")
        web = WebSearchCollector()
        results.extend(web.search(product_name))

        # 2. Händlerseiten
        print("🏪 Händlerseiten…")
        dealer = DealerSiteScanner()
        results.extend(dealer.scan_all())

        # 3. Foren
        print("💬 Foren…")
        forums = ForumPDFHunter()
        results.extend(forums.scan())

        # 4. Deep Scan (Top 10 URLs)
        print("🕵️ Deep Scan…")
        deep = DeepPDFScanner()
        for url in results[:10]:
            results.extend(deep.deep_scan(url))

        # Duplikate entfernen
        final = list(set(results))

        print(f"\n✅ Gefundene PDFs: {len(final)}")
        return final


# ============================================================
# 7. Beispiel
# ============================================================
if __name__ == "__main__":
    finder = UltimatePDFFinder()
    produkt = "LG Therma V R290 Monobloc"
    pdfs = finder.find(produkt)

    for p in pdfs:
        print(p)
