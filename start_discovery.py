import threading
import asyncio
from tkinter import Tk
from ravia_ki.ui.discovery_ui import DiscoveryUI
from ravia_ki.discovery.human_discovery_engine import HumanDiscoveryEngine


def run_async(coro):
    return asyncio.run(coro)


def on_discovery_start(manufacturer, series, power):
    print("==============================================")
    print(" Discovery gestartet ")
    print("==============================================")
    print(f"Hersteller: {manufacturer}")
    print(f"Serie:      {series}")
    print(f"Leistung:   {power}")
    print("----------------------------------------------")

    def worker():
        engine = HumanDiscoveryEngine()
        result = run_async(engine.discover(manufacturer.lower(), series, power))
        print(" Discovery Ergebnis:")
        print("----------------------------------------------")
        print(f"Gefundene Produktseiten: {result['count_pages']}")
        print(f"Gefundene PDFs:          {result['count_pdfs']}")
        for p in result["product_pages"]:
            print("PAGE:", p)
        for pdf in result["pdfs"]:
            print("PDF: ", pdf)
        print("==============================================")

    threading.Thread(target=worker, daemon=True).start()


def main():
    root = Tk()
    root.geometry("450x350")
    DiscoveryUI(root, on_discovery_start)
    root.mainloop()


if __name__ == "__main__":
    main()
