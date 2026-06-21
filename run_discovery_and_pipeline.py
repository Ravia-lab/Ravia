from ravia_ki.discovery.discovery_engine import DiscoveryEngine
from pipeline import Pipeline


def main():
    seed_urls = [
        "https://www.lg.com/global/business/air-solution",
        "https://www.panasonic.com/global/business/psna/air-conditioning.html",
        "https://www.daikin.eu/en_us/products.html",
        "https://www.vaillant.de/produkte/",
    ]

    engine = DiscoveryEngine()
    result = engine.discover(seed_urls)

    print("\n--- PDFs ---")
    for url in result["pdfs"]:
        print(url)

    pipeline = Pipeline()
    pipeline.process_urls(result["pdfs"])


if __name__ == "__main__":
    main()
