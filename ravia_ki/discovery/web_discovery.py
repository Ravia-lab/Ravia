import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class WebDiscovery:

    def __init__(self):
        self.visited = set()

    def crawl(self, start_url, max_depth=2):
        results = set()
        self._crawl_recursive(start_url, 0, max_depth, results)
        return results

    def _crawl_recursive(self, url, depth, max_depth, results):
        if depth > max_depth:
            return
        if url in self.visited:
            return

        self.visited.add(url)
        results.add(url)

        try:
            response = requests.get(url, timeout=5)
            if "text/html" not in response.headers.get("Content-Type", ""):
                return

            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                if self._same_domain(url, next_url):
                    self._crawl_recursive(next_url, depth + 1, max_depth, results)

        except:
            pass

    def _same_domain(self, base, target):
        return urlparse(base).netloc == urlparse(target).netloc
