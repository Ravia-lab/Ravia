import re
import fitz  # PyMuPDF


class PDFClassifier:

    # ---------------------------------------------------------
    # Schlüsselwörter für jede Kategorie
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # PDF-Text extrahieren
    # ---------------------------------------------------------
    def extract_text(self, pdf_path, max_pages=3):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for i in range(min(max_pages, len(doc))):
                text += doc[i].get_text()
            return text.lower()
        except Exception:
            return ""

    # ---------------------------------------------------------
    # Klassifikation anhand von Text + Dateiname
    # ---------------------------------------------------------
    def classify(self, pdf_path):
        filename = pdf_path.lower()
        text = self.extract_text(pdf_path)

        scores = {cat: 0 for cat in self.KEYWORDS}

        # Dateiname analysieren
        for category, words in self.KEYWORDS.items():
            for w in words:
                if w in filename:
                    scores[category] += 3  # Dateiname = starkes Signal

        # PDF-Text analysieren
        for category, words in self.KEYWORDS.items():
            for w in words:
                if w in text:
                    scores[category] += 1

        # Beste Kategorie bestimmen
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "unbekannt"

        return best

    # ---------------------------------------------------------
    # Mehrfachklassifikation (optional)
    # ---------------------------------------------------------
    def classify_multi(self, pdf_path, threshold=2):
        filename = pdf_path.lower()
        text = self.extract_text(pdf_path)

        results = []

        for category, words in self.KEYWORDS.items():
            score = 0

            for w in words:
                if w in filename:
                    score += 3
                if w in text:
                    score += 1

            if score >= threshold:
                results.append(category)

        return results if results else ["unbekannt"]
