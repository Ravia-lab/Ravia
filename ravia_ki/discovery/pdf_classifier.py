import re

CATEGORIES = {
    "fehlerliste": [
        r"error", r"fault", r"fehler", r"diagnostic", r"troubleshoot"
    ],
    "datenblatt": [
        r"datasheet", r"spec", r"technical", r"tds", r"data"
    ],
    "explosionszeichnung": [
        r"exploded", r"parts", r"spare", r"ersatzteil", r"component"
    ],
    "installationsanleitung": [
        r"installation", r"install", r"montage", r"setup"
    ],
    "bedienungsanleitung": [
        r"user", r"manual", r"bedien", r"operation", r"guide"
    ],
    "servicemanual": [
        r"service", r"repair", r"maintenance", r"wartung"
    ],
    "hydraulikschema": [
        r"hydraulic", r"schema", r"schematic", r"piping"
    ],
    "katalog": [
        r"catalog", r"brochure", r"marketing"
    ],
    "ersatzteile": [
        r"parts", r"spare", r"component"
    ],
}

def classify_pdf(url: str) -> str:
    u = url.lower()

    for category, patterns in CATEGORIES.items():
        for p in patterns:
            if re.search(p, u):
                return category

    return "unbekannt"
