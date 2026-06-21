import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------------------------------------------------------
# Hersteller- / Modell- / kW-Datenbank
# ---------------------------------------------------------
ALL_MANUFACTURERS = {
    "LG": {
        "Therma V Monoblock R290": [5, 7, 9, 12, 14, 16],
        "Therma V Split R32": [5, 7, 9, 12, 14, 16],
        "Therma V Monoblock R32": [5, 7, 9, 12, 14, 16],
        "Hydrokit": [3, 5, 7, 9],
        "Multi V": [4, 6, 8, 10, 12],
    },
    "Panasonic": {
        "Aquarea T-CAP": [5, 7, 9, 12, 16],
        "Aquarea High Performance": [5, 7, 9, 12, 16],
        "Aquarea Monoblock": [5, 7, 9, 12, 16],
        "Aquarea Split": [5, 7, 9, 12, 16],
    },
    "Daikin": {
        "Altherma 3 R": [4, 6, 8, 11, 14, 16],
        "Altherma 3 H HT": [8, 11, 14, 16],
        "Altherma Monoblock": [5, 7, 9, 11, 14],
    },
    "Vaillant": {
        "aroTHERM plus": [3, 5, 7, 10, 12],
        "aroTHERM split": [5, 7, 10, 12],
        "flexoTHERM": [5, 7, 10, 12],
    },
    "Viessmann": {
        "Vitocal 250-A": [2.5, 4, 6, 8, 10],
        "Vitocal 200-A": [4, 6, 8, 10, 12],
        "Vitocal 150-A": [4, 6, 8, 10],
    },
    "Wolf": {
        "CHA Monoblock": [7, 10],
        "BWL-1": [5, 7, 10],
        "BWL-2": [5, 7, 10],
    },
    "Nibe": {
        "F2120": [8, 12, 16],
        "S2125": [8, 12, 16],
    },
    "Stiebel": {
        "WPL 25": [5, 7, 10],
        "WPL 15": [5, 7],
        "HPA-O": [5, 7, 10],
    },
    "Weishaupt": {
        "WBB": [5, 7, 10],
        "WPL": [5, 7, 10],
    },
    "Buderus": {
        "Logatherm WLW196i": [6, 8, 10, 12],
        "Logatherm WLW176i": [6, 8, 10],
    },
}


@dataclass
class DiscoveryResult:
    product_pages: list
    datasheets: list
    manuals: list
    errorcode_lists: list
    hydraulik_schemas: list
    images: list
    zip_files: list


class WebDiscovery:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0"}

        self.manufacturers = list(ALL_MANUFACTURERS.keys())
        self.known_models = ALL_MANUFACTURERS

        self.search_cache = {}
        self.redirect_cache = {}

    # ---------------- Hersteller / Modelle / kW ----------------

    def get_manufacturers(self):
        return self.manufacturers

    def get_models_for_manufacturer(self, manufacturer: str) -> list:
        return list(self.known_models.get(manufacturer, {}).keys())

    def get_kw_for_model(self, manufacturer: str, model: str) -> list:
        return self.known_models.get(manufacturer, {}).get(model, [])

    # ---------------- URL / Redirect / Caching ----------------

    def normalize_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            clean = parsed._replace(query="", fragment="")
            return urlunparse(clean)
        except:
            return url

    def resolve_redirect_single(self, url: str) -> str:
        if url in self.redirect_cache:
            return self.redirect_cache[url]

        try:
            r = self.session.get(url, headers=self.headers, timeout=5, allow_redirects=True)
            real = r.url
        except:
            real = url

        self.redirect_cache[url] = real
        return real

    def resolve_redirects_parallel(self, urls: list, max_workers: int = 10) -> list:
        resolved = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(self.resolve_redirect_single, u): u for u in urls}
            for future in as_completed(future_map):
                try:
                    real = future.result()
                    resolved.append(real)
                except:
                    pass
        return resolved

    # ---------------- Suchmaschinen ----------------

    def search_bing(self, query: str) -> list:
        try:
            url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("li.b_algo h2 a") if a.get("href")]
        except:
            return []

    def search_duckduckgo(self, query: str) -> list:
        try:
            url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("a.result__a") if a.get("href")]
        except:
            return []

    def search_google(self, query: str) -> list:
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            links = []
            for a in soup.select("a"):
                href = a.get("href", "")
                if href.startswith("/url?q="):
                    real = href.split("/url?q=")[1].split("&")[0]
                    links.append(real)
            return links
        except:
            return []

    def search_yahoo(self, query: str) -> list:
        try:
            url = f"https://search.yahoo.com/search?p={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("h3.title a") if a.get("href")]
        except:
            return []

    def search_startpage(self, query: str) -> list:
        try:
            url = f"https://www.startpage.com/sp/search?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("a.result-link") if a.get("href")]
        except:
            return []

    def search_ecosia(self, query: str) -> list:
        try:
            url = f"https://www.ecosia.org/search?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("a.result-title") if a.get("href")]
        except:
            return []

    def search_brave(self, query: str) -> list:
        try:
            url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("a") if a.get("href") and "http" in a.get("href")]
        except:
            return []

    def search_qwant(self, query: str) -> list:
        try:
            url = f"https://www.qwant.com/?q={query.replace(' ', '+')}"
            r = self.session.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            return [a.get("href") for a in soup.select("a") if a.get("href") and "http" in a.get("href")]
        except:
            return []

    # ---------------- Multi-Search mit Cache + Threading ----------------

    def search(self, query: str) -> list:
        if query in self.search_cache:
            return self.search_cache[query]

        search_funcs = [
            self.search_bing,
            self.search_duckduckgo,
            self.search_google,
            self.search_yahoo,
            self.search_startpage,
            self.search_ecosia,
            self.search_brave,
            self.search_qwant,
        ]

        urls = []

        with ThreadPoolExecutor(max_workers=len(search_funcs)) as executor:
            futures = {executor.submit(func, query): func for func in search_funcs}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    urls.extend(result)
                except:
                    pass

        urls = list(set(urls))
        self.search_cache[query] = urls
        return urls

    # ---------------- Haupt-Discovery ----------------

    def discover_device(self, manufacturer: str, model: str, kw: str, mode="all") -> DiscoveryResult:
        search_terms = [
            f"{manufacturer} {model} {kw} kW",
            f"{manufacturer} {model} {kw} kW PDF",
            f"{manufacturer} {model} {kw} kW Manual",
            f"{manufacturer} {model} {kw} kW Service",
            f"{manufacturer} {model} {kw} kW Fehlercode",
            f"{manufacturer} {model} {kw} kW Hydraulic Diagram",
        ]

        raw_urls = []
        for term in search_terms:
            raw_urls.extend(self.search(term))

        normalized = [self.normalize_url(u) for u in raw_urls if u.startswith("http")]
        resolved = self.resolve_redirects_parallel(normalized, max_workers=15)
        all_urls = list(set(resolved))

        pdfs = [u for u in all_urls if u.lower().endswith(".pdf")]
        zips = [u for u in all_urls if u.lower().endswith(".zip")]
        images = [u for u in all_urls if u.lower().endswith((".jpg", ".jpeg", ".png"))]
        html = [u for u in all_urls if not u.lower().endswith((".pdf", ".zip"))]

        return DiscoveryResult(
            product_pages=html,
            datasheets=pdfs,
            manuals=pdfs,
            errorcode_lists=pdfs,
            hydraulik_schemas=pdfs,
            images=images,
            zip_files=zips,
        )
