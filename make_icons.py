"""
RaVia Heizlast UI mit automatischer Icon-Erkennung und -Ladung.
Leg die Quelldatei mit dem Basisnamen "ravia" (z. B. ravia.png, ravia.jpg, ravia.webp, ravia.svg)
in dasselbe Verzeichnis wie dieses Skript. Das Programm versucht, passende Icons aus icons/ zu laden.
Optional: Pillow und cairosvg werden verwendet, falls du Icon-Generierung direkt aus dem UI starten willst.
"""

import json
import os
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox
)
from PySide6.QtGui import QPixmap, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QSize

# Optional: Pillow / cairosvg für lokale Icon-Erzeugung (falls installiert)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except Exception:
    CAIROSVG_AVAILABLE = False

# ---------------- Konfiguration ----------------
DATA_FILE = "ravia_data.json"
SRC_BASENAME = "ravia"  # Basisname deiner Quelldatei (ohne Endung)
ICON_DIR = "icons"
ICON_SIZES = [16, 32, 48, 64, 128, 256, 512]
ICO_SIZES = [16, 32, 48, 128]  # für .ico

# ---------------- Hilfsfunktionen für Daten ----------------
def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# ---------------- Icon-Erkennung / Erzeugung ----------------
POSSIBLE_EXT = [".png", ".jpg", ".jpeg", ".webp", ".svg"]

def find_source(basename):
    for ext in POSSIBLE_EXT:
        path = basename + ext
        if os.path.exists(path):
            return path
    return None

def svg_to_png(svg_path, out_png):
    if not CAIROSVG_AVAILABLE:
        return False
    try:
        cairosvg.svg2png(url=svg_path, write_to=out_png)
        return True
    except Exception:
        return False

def generate_icons_from_source():
    """
    Versucht, aus der Quelldatei 'ravia' (mit möglicher Endung) die Icon-Varianten zu erzeugen.
    Funktioniert nur, wenn Pillow installiert ist. Für SVG wird cairosvg benötigt.
    Diese Funktion ist optional und wird nicht automatisch aufgerufen — sie kann bei Bedarf
    manuell aktiviert werden.
    """
    if not PIL_AVAILABLE:
        print("Pillow nicht installiert. Installiere mit: pip install pillow")
        return False

    src = find_source(SRC_BASENAME)
    if not src:
        print("Keine Quelldatei mit Basisnamen 'ravia' gefunden.")
        return False

    tmp_png = None
    ext = os.path.splitext(src)[1].lower()
    try:
        if ext == ".svg":
            tmp_png = SRC_BASENAME + "_tmp.png"
            ok = svg_to_png(src, tmp_png)
            if not ok:
                print("SVG gefunden, aber cairosvg fehlt oder Konvertierung schlug fehl.")
                return False
            im = Image.open(tmp_png).convert("RGBA")
        else:
            im = Image.open(src).convert("RGBA")
    except Exception as e:
        print("Fehler beim Laden der Quelldatei:", e)
        if tmp_png and os.path.exists(tmp_png):
            try: os.remove(tmp_png)
            except Exception: pass
        return False

    # Quadrat-Canvas zentrieren
    max_side = max(im.width, im.height)
    canvas = Image.new("RGBA", (max_side, max_side), (0,0,0,0))
    offset = ((max_side - im.width)//2, (max_side - im.height)//2)
    canvas.paste(im, offset, im)

    os.makedirs(ICON_DIR, exist_ok=True)
    for s in ICON_SIZES:
        out_path = os.path.join(ICON_DIR, f"ravia_icon_{s}.png")
        resized = canvas.resize((s, s), Image.LANCZOS)
        try:
            resized.save(out_path, optimize=True)
        except Exception:
            resized.save(out_path)
        print("Saved", out_path)

    # optional .ico
    try:
        imgs = []
        for s in ICO_SIZES:
            p = os.path.join(ICON_DIR, f"ravia_icon_{s}.png")
            if os.path.exists(p):
                imgs.append(Image.open(p))
        if imgs:
            ico_path = os.path.join(ICON_DIR, "ravia_icon.ico")
            imgs[0].save(ico_path, format="ICO", sizes=[(i.width, i.height) for i in imgs])
            print("Saved", ico_path)
    except Exception:
        pass

    if tmp_png and os.path.exists(tmp_png):
        try: os.remove(tmp_png)
        except Exception: pass

    return True

def get_best_icon_path():
    """
    Gibt den besten vorhandenen Icon-Pfad zurück (bevorzugt 128px PNG, sonst nächstgrößer).
    """
    if not os.path.exists(ICON_DIR):
        return None
    preferred = [128, 64, 48, 32, 16]
    for s in preferred:
        p = os.path.join(ICON_DIR, f"ravia_icon_{s}.png")
        if os.path.exists(p):
            return p
    ico = os.path.join(ICON_DIR, "ravia_icon.ico")
    if os.path.exists(ico):
        return ico
    return None

# ---------------- Beispiel-Berechnungsfunktion (Platzhalter) ----------------
# Hier wird die Heizlast-Berechnung referenziert. Ersetze oder erweitere diese Funktion
# durch deine tatsächliche Berechnungslogik (z. B. import aus Heizlast.py).
def berechne_gesamtleistung(plz, flaeche, raumhoehe, baujahr, verglasung,
                            daemmung, anzahl_hk, gemischt, puffer, personen, speicher):
    # Platzhalter-Logik: einfache Näherung für Demo-Zwecke
    u_gesamt = 1.82  # Beispielwert
    delta_t = 30
    heizlast = max(0.5, flaeche * 0.01 * (30 - (2026 - baujahr) * 0.01))
    warmwasser = 0.5 if personen > 0 else 0.0
    puffer_verluste = 0.0 if puffer == 0 else 0.02 * puffer / 100.0
    gesamt = heizlast + warmwasser + puffer_verluste
    return {
        "u_gesamt": u_gesamt,
        "delta_t": delta_t,
        "heizlast": heizlast,
        "warmwasser": warmwasser,
        "puffer": puffer_verluste,
        "gesamt": gesamt
    }

# ---------------- UI ----------------
class HeizlastUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RaVia Heizlast – PySide6 UI")

        # Layout
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setHorizontalSpacing(10)
        self.layout.setVerticalSpacing(8)

        # Farbpalette und Stylesheet passend zum RaVia-Design
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0A0F1F"))
        palette.setColor(QPalette.WindowText, QColor("#E8F1F8"))
        palette.setColor(QPalette.Base, QColor("#1A2233"))
        palette.setColor(QPalette.Text, QColor("#E8F1F8"))
        palette.setColor(QPalette.Button, QColor("#1A2233"))
        palette.setColor(QPalette.ButtonText, QColor("#00E5E5"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QWidget {
                background-color: #0A0F1F;
                color: #E8F1F8;
                font-size: 13px;
                font-family: "Segoe UI", Roboto, Arial, sans-serif;
            }
            QLabel {
                color: #A9E9E9;
            }
            QLineEdit, QComboBox {
                background-color: #121826;
                border: 1px solid #0FBFC0;
                padding: 6px;
                border-radius: 6px;
                color: #E8F1F8;
                min-height: 26px;
            }
            QPushButton {
                background-color: #0F1624;
                border: 1px solid #00E5E5;
                padding: 8px;
                border-radius: 8px;
                color: #00E5E5;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0B1220;
                border: 1px solid #F2C14E;
                color: #F2C14E;
            }
            QTextEdit {
                background-color: #0F1724;
                border: 1px solid #00E5E5;
                padding: 8px;
                border-radius: 8px;
                color: #E8F1F8;
            }
        """)

        # Logo (wenn vorhanden) zentriert oben
        row = 0
        best_icon = get_best_icon_path()
        if best_icon:
            try:
                logo = QLabel()
                pixmap = QPixmap(best_icon).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo.setPixmap(pixmap)
                logo.setAlignment(Qt.AlignCenter)
                self.layout.addWidget(logo, row, 0, 1, 2, alignment=Qt.AlignCenter)
                row += 1
            except Exception:
                pass

        # Felder-Container
        self.fields = {}

        # PLZ
        self.layout.addWidget(QLabel("PLZ"), row, 0)
        self.fields["plz"] = QLineEdit()
        self.fields["plz"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["plz"], row, 1)
        row += 1

        # Wohnfläche
        self.layout.addWidget(QLabel("Wohnfläche (m²)"), row, 0)
        self.fields["flaeche"] = QLineEdit()
        self.fields["flaeche"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["flaeche"], row, 1)
        row += 1

        # Raumhöhe
        self.layout.addWidget(QLabel("Raumhöhe (m)"), row, 0)
        self.fields["raumhoehe"] = QLineEdit()
        self.fields["raumhoehe"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["raumhoehe"], row, 1)
        row += 1

        # Baujahr
        self.layout.addWidget(QLabel("Baujahr"), row, 0)
        self.fields["baujahr"] = QLineEdit()
        self.fields["baujahr"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["baujahr"], row, 1)
        row += 1

        # Verglasung
        self.layout.addWidget(QLabel("Verglasung"), row, 0)
        self.fields["verglasung"] = QComboBox()
        self.fields["verglasung"].addItems([
            "1 - Einfachverglasung (schlecht)",
            "2 - Doppelverglasung (normal)",
            "3 - Dreifachverglasung (sehr gut)"
        ])
        self.fields["verglasung"].currentIndexChanged.connect(self.auto_save)
        self.layout.addWidget(self.fields["verglasung"], row, 1)
        row += 1

        # Dämmung
        self.layout.addWidget(QLabel("Gebäudedämmung"), row, 0)
        self.fields["daemmung"] = QComboBox()
        self.fields["daemmung"].addItems([
            "1 - keine Dämmung (Altbau)",
            "2 - teilweise gedämmt",
            "3 - gut gedämmt (modern)"
        ])
        self.fields["daemmung"].currentIndexChanged.connect(self.auto_save)
        self.layout.addWidget(self.fields["daemmung"], row, 1)
        row += 1

        # Heizkreis 1
        self.layout.addWidget(QLabel("Heizkreis 1"), row, 0)
        self.fields["hk1"] = QComboBox()
        self.fields["hk1"].addItems([
            "Heizkörper",
            "Fußbodenheizung"
        ])
        self.fields["hk1"].currentIndexChanged.connect(self.auto_save)
        self.layout.addWidget(self.fields["hk1"], row, 1)
        row += 1

        # Heizkreis 2
        self.layout.addWidget(QLabel("Heizkreis 2"), row, 0)
        self.fields["hk2"] = QComboBox()
        self.fields["hk2"].addItems([
            "kein zweiter Heizkreis",
            "Heizkörper",
            "Fußbodenheizung"
        ])
        self.fields["hk2"].currentIndexChanged.connect(self.auto_save)
        self.layout.addWidget(self.fields["hk2"], row, 1)
        row += 1

        # Puffer
        self.layout.addWidget(QLabel("Pufferspeicher (L)"), row, 0)
        self.fields["puffer"] = QLineEdit()
        self.fields["puffer"].setPlaceholderText("leer = kein Puffer")
        self.fields["puffer"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["puffer"], row, 1)
        row += 1

        # Personen
        self.layout.addWidget(QLabel("Personen"), row, 0)
        self.fields["personen"] = QLineEdit()
        self.fields["personen"].setPlaceholderText("leer = keine Warmwasserbereitung")
        self.fields["personen"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["personen"], row, 1)
        row += 1

        # Speicher
        self.layout.addWidget(QLabel("Brauchwasserspeicher (L)"), row, 0)
        self.fields["speicher"] = QLineEdit()
        self.fields["speicher"].setPlaceholderText("leer = kein Speicher vorhanden")
        self.fields["speicher"].editingFinished.connect(self.auto_save)
        self.layout.addWidget(self.fields["speicher"], row, 1)
        row += 1

        # Buttons
        self.btn = QPushButton("Berechnen")
        self.btn.clicked.connect(self.berechnen)
        self.layout.addWidget(self.btn, row, 0, 1, 2)
        row += 1

        self.clear_btn = QPushButton("Neueingabe / Löschen")
        self.clear_btn.clicked.connect(self.clear_fields)
        self.layout.addWidget(self.clear_btn, row, 0, 1, 2)
        row += 1

        # Ausgabe
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(140)
        self.layout.addWidget(self.output, row, 0, 1, 2)

        # Lade gespeicherte Werte (falls vorhanden)
        self.load_saved_values()

    # ---------------- Mischungslogik ----------------
    def bestimme_mischung(self):
        hk1 = self.fields["hk1"].currentText()
        hk2 = self.fields["hk2"].currentText()

        if hk2 == "kein zweiter Heizkreis":
            return 1 if hk1 == "Fußbodenheizung" else 2

        if hk1 == "Heizkörper" and hk2 == "Heizkörper":
            return 2

        if hk1 == "Fußbodenheizung" and hk2 == "Fußbodenheizung":
            return 1

        return 1  # Mischsystem

    # ---------------- Hilfsfunktionen ----------------
    def get_int_value(self, field):
        text = field.text().strip()
        if text == "":
            return 0
        try:
            return int(text)
        except ValueError:
            return 0

    def auto_save(self):
        data = {}
        for key, field in self.fields.items():
            if isinstance(field, QLineEdit):
                data[key] = field.text()
            else:
                data[key] = field.currentIndex()
        save_data(data)

    def load_saved_values(self):
        data = load_data()
        for key, field in self.fields.items():
            if key in data:
                if isinstance(field, QLineEdit):
                    field.setText(str(data[key]))
                else:
                    try:
                        field.setCurrentIndex(int(data[key]))
                    except Exception:
                        pass

    # ---------------- Berechnung ----------------
    def berechnen(self):
        try:
            plz = int(self.fields["plz"].text())
            flaeche = float(self.fields["flaeche"].text())
            raumhoehe = float(self.fields["raumhoehe"].text())
            baujahr = int(self.fields["baujahr"].text())
        except Exception:
            self.output.setText("❌ Fehler: Bitte PLZ, Fläche, Raumhöhe und Baujahr korrekt ausfüllen.")
            return

        verglasung = self.fields["verglasung"].currentIndex() + 1
        daemmung = self.fields["daemmung"].currentIndex() + 1

        hk2_index = self.fields["hk2"].currentIndex()
        anzahl_hk = 1 if hk2_index == 0 else 2

        gemischt = self.bestimme_mischung()

        puffer = self.get_int_value(self.fields["puffer"])
        personen = self.get_int_value(self.fields["personen"])
        speicher = self.get_int_value(self.fields["speicher"])

        result = berechne_gesamtleistung(
            plz, flaeche, raumhoehe, baujahr, verglasung,
            daemmung, anzahl_hk, gemischt,
            puffer, personen, speicher
        )

        text = f"""U-Wert gesamt: {result['u_gesamt']:.3f} W/m²K
Auslegungstemperatur ΔT: {result['delta_t']} K

Heizlast (ohne Speicher): {result['heizlast']:.2f} kW
Warmwasser: {result['warmwasser']:.2f} kW
Pufferspeicher-Verluste: {result['puffer']:.2f} kW

Gesamtleistung: {result['gesamt']:.2f} kW
"""
        self.output.setText(text)

    # ---------------- Felder löschen ----------------
    def clear_fields(self):
        for field in self.fields.values():
            if isinstance(field, QLineEdit):
                field.clear()
            else:
                field.setCurrentIndex(0)

        if os.path.exists(DATA_FILE):
            try:
                os.remove(DATA_FILE)
            except Exception:
                pass

        self.output.clear()

# ------------------- Start -------------------
def main():
    app = QApplication([])

    # Falls Icons noch nicht existieren und Pillow verfügbar ist, kannst du hier
    # die automatische Erzeugung aktivieren, indem du die nächste Zeile entkommentierst.
    # Achtung: das erzeugt Dateien im Ordner icons/.
    #
    # if PIL_AVAILABLE:
    #     generate_icons_from_source()

    window = HeizlastUI()
    window.resize(520, 720)

    # Fenstericon setzen (falls vorhanden)
    icon_path = get_best_icon_path()
    if icon_path:
        try:
            window.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

    window.show()
    app.exec()

if __name__ == "__main__":
    main()
