import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class PDFFinder:

    def extract_pdfs(self, url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            pdfs = []
            for link in soup.find_all("a", href=True):
                href = link["href"].lower()
                if href.endswith(".pdf"):
                    pdfs.append(urljoin(url, href))

            return pdfs

        except:
            return []
