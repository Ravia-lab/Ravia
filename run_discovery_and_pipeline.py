from ravia_ki.ui.discovery_ui import DiscoveryUI
from ravia_ki.ui.document_filter_ui import DocumentFilterUI
from ravia_ki.discovery.discovery_engine import DiscoveryEngine
import tkinter as tk

def start_discovery(manufacturer, series, power):
    print("Starte Discovery:", manufacturer, series, power)
    engine = DiscoveryEngine()
    result = engine.discover_manufacturer(manufacturer.lower())

    pdfs = result["pdfs"]

    filter_window = tk.Toplevel()
    DocumentFilterUI(filter_window, pdfs)

def main():
    root = tk.Tk()
    DiscoveryUI(root, start_discovery)
    root.mainloop()

if __name__ == "__main__":
    main()
