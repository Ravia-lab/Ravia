import json
import logging
from datetime import datetime

from ravia_ki.discovery.discovery_engine import DiscoveryEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    print("\n============================================")
    print("   RAVIA – GLOBAL DISCOVERY ENGINE 5.0")
    print("============================================\n")

    engine = DiscoveryEngine(max_workers=6)

    print("[INFO] Starte parallele Discovery aller Hersteller...\n")
    results = engine.discover_all_parallel()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"discovery_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\n============================================")
    print("   DISCOVERY ABGESCHLOSSEN")
    print("============================================\n")

    print(f"Ergebnisse gespeichert in: {output_file}\n")

    # Kurze Zusammenfassung
    for r in results:
        manu = r["manufacturer"]
        pdf_count = len(r["pdfs"])
        ok_count = sum(1 for p in r["pdfs"] if p["pipeline_status"]["status"] == "ok")
        print(f"- {manu}: {pdf_count} PDFs gefunden, {ok_count} erfolgreich verarbeitet")

    print("\nFertig.\n")


if __name__ == "__main__":
    main()
