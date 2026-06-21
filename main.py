import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox
)
from PySide6.QtGui import QPixmap, QIcon, QPalette, QColor
from PySide6.QtCore import Qt

from Heizlast import berechne_heizlast_din
from raum_editor import RoomEditor
from bauteile_editor import BauteileEditor
from lueftungs_editor import LueftungEditor
from heizlast_raeume_ui import RaumHeizlastUI


# ---------------------------------------------------------
# Hilfsfunktionen für Icons (PyInstaller kompatibel)
# ---------------------------------------------------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_best_icon_path():
    preferred = [128, 64, 48, 32, 16]
    for s in preferred:
        p = resource_path(f"icons/ravia_icon_{s}.png")
        if os.path.exists(p):
            return p
    ico = resource_path("icons/ravia_icon.ico")
    if os.path.exists(ico):
        return ico
    return None


# ---------------------------------------------------------
# Hauptfenster
# ---------------------------------------------------------
class HeizlastUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RaVia – Heizlast nach DIN EN 12831")

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)

        # -----------------------------
        # Dark Theme
        # -----------------------------
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0A0F1F"))
        palette.setColor(QPalette.WindowText, QColor("#E8F1F8"))
        palette.setColor(QPalette.Base, QColor("#1A2233"))
        palette.setColor(QPalette.Text, QColor("#E8F1F8"))
        palette.setColor(QPalette.Button, QColor("#1A2233"))
        palette.setColor(QPalette.ButtonText, QColor("#00E5E5"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QWidget { background-color: #0A0F1F; color: #E8F1F8; }
            QLabel { color: #A9E9E9; }
            QLineEdit, QComboBox {
                background-color: #121826;
                border: 1px solid #0FBFC0;
                padding: 6px;
                border-radius: 6px;
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
            }
        """)

        # -----------------------------
        # Eingabefelder
        # -----------------------------
        row = 0
        self.fields = {}

        def add(label, key, widget):
            nonlocal row
            self.layout.addWidget(QLabel(label), row, 0)
            self.fields[key] = widget
            self.layout.addWidget(widget, row, 1)
            row += 1

        # Logo
        icon_path = get_best_icon_path()
        if icon_path:
            logo = QLabel()
            pixmap = QPixmap(icon_path).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(logo, row, 0, 1, 2)
            row += 1

        add("PLZ", "plz", QLineEdit())
        add("Wohnfläche (m²)", "flaeche", QLineEdit())
        add("Raumhöhe (m)", "raumhoehe", QLineEdit())
        add("Baujahr", "baujahr", QLineEdit())

        daemmung = QComboBox()
        daemmung.addItems(["keine Dämmung", "teilweise gedämmt", "gut gedämmt"])
        add("Dämmstandard", "daemmung", daemmung)

        add("Personen", "personen", QLineEdit())
        add("Pufferspeicher (L)", "puffer", QLineEdit())

        # -----------------------------
        # Buttons
        # -----------------------------
        self.btn = QPushButton("Gebäude-Heizlast berechnen")
        self.btn.clicked.connect(self.berechnen)
        self.layout.addWidget(self.btn, row, 0, 1, 2)
        row += 1

        self.clear_btn = QPushButton("Neueingabe / Löschen")
        self.clear_btn.clicked.connect(self.clear_fields)
        self.layout.addWidget(self.clear_btn, row, 0, 1, 2)
        row += 1

        self.btn_rooms = QPushButton("Räume verwalten")
        self.btn_rooms.clicked.connect(self.open_rooms)
        self.layout.addWidget(self.btn_rooms, row, 0, 1, 2)
        row += 1

        self.btn_bauteile = QPushButton("Bauteile (DIN‑PRO)")
        self.btn_bauteile.clicked.connect(self.open_bauteile)
        self.layout.addWidget(self.btn_bauteile, row, 0, 1, 2)
        row += 1

        self.btn_lueftung = QPushButton("Lüftung bearbeiten")
        self.btn_lueftung.clicked.connect(self.open_lueftung)
        self.layout.addWidget(self.btn_lueftung, row, 0, 1, 2)
        row += 1

        self.btn_raum_heizlast = QPushButton("Raum-Heizlast (Diagramm)")
        self.btn_raum_heizlast.clicked.connect(self.open_raum_heizlast)
        self.layout.addWidget(self.btn_raum_heizlast, row, 0, 1, 2)
        row += 1

        # -----------------------------
        # Ausgabe
        # -----------------------------
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output, row, 0, 1, 2)

    # ---------------------------------------------------------
    # Gebäude-Heizlast
    # ---------------------------------------------------------
    def berechnen(self):
        try:
            plz = int(self.fields["plz"].text())
            flaeche = float(self.fields["flaeche"].text())
            raumhoehe = float(self.fields["raumhoehe"].text())
            baujahr = int(self.fields["baujahr"].text())
        except Exception:
            self.output.setText("❌ Bitte PLZ, Fläche, Raumhöhe und Baujahr korrekt eingeben.")
            return

        daemmung = self.fields["daemmung"].currentIndex() + 1
        personen = int(self.fields["personen"].text() or 0)
        puffer = int(self.fields["puffer"].text() or 0)

        result = berechne_heizlast_din(
            plz, flaeche, raumhoehe, baujahr,
            daemmung, personen, puffer
        )

        self.output.setText(
            f"<b>Normaußentemperatur:</b> {result['nat']} °C\n"
            f"<b>ΔT:</b> {result['delta_t']} K\n"
            f"<b>U-Wert (geschätzt):</b> {result['u_gesamt']} W/m²K\n"
            f"<b>Luftwechsel n:</b> {result['luftwechsel']}\n\n"
            f"<b>Transmissionswärmeverlust Qₜ:</b> {result['q_t']} W\n"
            f"<b>Lüftungswärmeverlust Qᵥ:</b> {result['q_v']} W\n\n"
            f"<b>Heizlast Gebäude:</b> {result['heizlast_geb']} kW\n"
            f"<b>Warmwasser:</b> {result['warmwasser']} kW\n"
            f"<b>Pufferverluste:</b> {result['puffer']} kW\n\n"
            f"<b>Gesamtleistung:</b> {result['gesamt']} kW"
        )

    # ---------------------------------------------------------
    # Editor-Fenster öffnen
    # ---------------------------------------------------------
    def open_rooms(self):
        self.room_editor = RoomEditor()
        self.room_editor.show()

    def open_bauteile(self):
        self.bauteile_editor = BauteileEditor()
        self.bauteile_editor.show()

    def open_lueftung(self):
        self.lueftung_editor = LueftungEditor()
        self.lueftung_editor.show()

    def open_raum_heizlast(self):
        try:
            plz = int(self.fields["plz"].text())
        except Exception:
            self.output.setText("❌ Bitte PLZ eingeben, um NAT zu bestimmen.")
            return

        nat_map = {
            "0": -12, "1": -12, "2": -10, "3": -12, "4": -10,
            "5": -10, "6": -14, "7": -14, "8": -16, "9": -16
        }
        nat = nat_map.get(str(plz)[0], -12)

        self.raum_heizlast_ui = RaumHeizlastUI(nat)
        self.raum_heizlast_ui.show()

    # ---------------------------------------------------------
    # Felder löschen
    # ---------------------------------------------------------
    def clear_fields(self):
        for f in self.fields.values():
            if isinstance(f, QLineEdit):
                f.clear()
            elif isinstance(f, QComboBox):
                f.setCurrentIndex(0)
        self.output.clear()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    window = HeizlastUI()

    icon_path = get_best_icon_path()
    if icon_path:
        window.setWindowIcon(QIcon(icon_path))

    window.resize(560, 840)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()