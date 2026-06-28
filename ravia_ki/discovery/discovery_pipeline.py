from ravia_ki.discovery.downloader import PDFDownloader
from ravia_ki.discovery.pdf_classifier import PDFClassifier
from ravia_ki.discovery.manufacturer_profiles import MANUFACTURER_PROFILES


class DiscoveryPipeline:
    """
    Minimal funktionierende DiscoveryPipeline für RaVia.
    Sammelt PDF-Links aus Herstellerprofilen, lädt sie herunter,
    klassifiziert sie und gibt die Ergebnisse zurück.
    """

    def __init__(self):
        self.downloader = PDFDownloader()
        self.classifier = PDFClassifier()

    def run(self, manufacturer: str):
        """
        Führt die Discovery für einen Hersteller aus.
        """
        if manufacturer not in MANUFACTURER_PROFILES:
            raise ValueError(f"Unbekannter Hersteller: {manufacturer}")

        urls = MANUFACTURER_PROFILES[manufacturer]

        results = []

        for url in urls:
            local_path = self.downloader.download(url)
            if not local_path:
                continue

            category = self.classifier.classify(local_path)

            results.append({
                "url": url,
                "local_path": local_path,
                "category": category,
            })

        return results
