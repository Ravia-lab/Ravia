import os

class PDFClassifier:
    """
    Minimaler PDF-Classifier ohne PyMuPDF.
    Klassifiziert PDFs nur anhand des Dateinamens.
    """

    def classify(self, path: str) -> str:
        filename = os.path.basename(path).lower()

        if "install" in filename or "montage" in filename:
            return "Installationsanleitung"
        if "service" in filename or "wartung" in filename:
            return "Service"
        if "hydraulik" in filename or "schema" in filename:
            return "Hydraulikplan"
        if "datenblatt" in filename or "spec" in filename:
            return "Datenblatt"

        return "Unbekannt"
