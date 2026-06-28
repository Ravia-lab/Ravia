import ravia_ki.database.plz_db
print("PYCHARM LÄDT:", ravia_ki.database.plz_db.__file__)

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QVBoxLayout, QHBoxLayout, QScrollArea
)
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtCore import Qt

from ravia_ki.engine.Heizlast import berechne_heizlast_din
from ravia_ki.data.rooms import load_rooms, save_rooms
from ravia_ki.ui.heizlast_raeume_ui import RaumHeizlastUI
from ravia_ki.utils.icons import get_best_icon_path

from ravia_ki.database.plz_db import get_plz_info, update_city


class HeizlastUI(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)

        # Dark Theme
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

        # PLZ + Auto-Felder
        add("PLZ", "plz", QLineEdit())

        # ⭐ FIX: PLZ automatisch abfragen
        self.fields["plz"].textChanged.connect(self.resolve_plz_data)
        self.fields["plz"].returnPressed.connect(self.resolve_plz_data)

        add("Ort / Stadt", "stadt", QLineEdit())
        add("Bundesland", "bundesland", QLineEdit())
        self.fields["bundesland"].setReadOnly(True)

        # PLZ-Felder leeren
        self.fields["stadt"].setText("")
        self.fields["bundesland"].setText("")

        # Button: Stadt speichern
        self.btn_save_city = QPushButton("Ort speichern")
        self.btn_save_city.clicked.connect(self.save_city)
        self.layout.addWidget(self.btn_save_city, row, 0, 1, 2)
        row += 1

        # Gebäude-Daten
        add("Wohnfläche (m²)", "flaeche", QLineEdit())
        add("Raumhöhe (m)", "raumhoehe", QLineEdit())
        add("Baujahr", "baujahr", QLineEdit())

        daemmung = QComboBox()
        daemmung.addItems(["keine Dämmung", "teilweise gedämmt", "gut gedämmt"])
        add("Dämmstandard", "daemmung", daemmung)

        add("Personen", "personen", QLineEdit())
        add("Pufferspeicher (L)", "puffer", QLineEdit())

        # Räume
        self.layout.addWidget(QLabel("Anzahl Räume:"), row, 0)
        self.room_count = QLineEdit()
        self.layout.addWidget(self.room_count, row, 1)
        row += 1

        self.room_count.returnPressed.connect(self.generate_room_fields)

        self.generate_rooms_btn = QPushButton("Räume erzeugen")
        self.generate_rooms_btn.clicked.connect(self.generate_room_fields)
        self.layout.addWidget(self.generate_rooms_btn, row, 0, 1, 2)
        row += 1

        # Scrollbereich
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll, row, 0, 1, 2)
        row += 1

        # ⭐ FIX: Räume NICHT automatisch laden
        self.rooms = []
        self.room_fields = []

        # Buttons
        self.btn = QPushButton("Gebäude-Heizlast berechnen")
        self.btn.clicked.connect(self.berechnen)
        self.layout.addWidget(self.btn, row, 0, 1, 2)
        row += 1

        self.btn_raum_heizlast = QPushButton("Raum-Heizlast (Diagramm)")
        self.btn_raum_heizlast.clicked.connect(self.open_raum_heizlast)
        self.layout.addWidget(self.btn_raum_heizlast, row, 0, 1, 2)
        row += 1

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output, row, 0, 1, 2)

        # ⭐ FIX: PLZ sofort beim Start abfragen
        self.resolve_plz_data()


    # PLZ → Ort/Bundesland
    def resolve_plz_data(self):
        plz = self.fields["plz"].text().strip()

        if len(plz) not in (4, 5) or not plz.isdigit():
            self.fields["stadt"].setText("Ungültige PLZ")
            self.fields["bundesland"].setText("")
            return

        info = get_plz_info(plz)

        if not info:
            self.fields["stadt"].setText("Unbekannt")
            self.fields["bundesland"].setText("")
            return

        self.fields["stadt"].setText(info["ort"] or "")
        self.fields["bundesland"].setText(info["bundesland"])


    # Stadt speichern
    def save_city(self):
        plz = self.fields["plz"].text().strip()
        new_city = self.fields["stadt"].text().strip()

        if not plz.isdigit():
            self.output.setText("❌ PLZ ungültig.")
            return

        update_city(plz, new_city)
        self.output.setText(f"✔ Ort für PLZ {plz} gespeichert: {new_city}")


    # Räume löschen
    def clear_room_fields(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)

            if item.layout():
                inner = item.layout()
                while inner.count():
                    w = inner.takeAt(0).widget()
                    if w:
                        w.deleteLater()

            if item.widget():
                item.widget().deleteLater()


    # Räume erzeugen
    def generate_room_fields(self):
        try:
            count = int(self.room_count.text())
        except:
            return

        self.clear_room_fields()
        self.room_fields = []

        DIN_TYPES = {
            "Wohnraum (20°C)": 20,
            "Schlafzimmer (18°C)": 18,
            "Küche (20°C)": 20,
            "Bad (24°C)": 24,
            "WC (18°C)": 18,
            "Flur (15°C)": 15,
            "Abstellraum (12°C)": 12,
            "Technikraum (10°C)": 10,
            "Keller beheizt (12°C)": 12,
            "Keller unbeheizt (10°C)": 10
        }

        for i in range(count):
            row = QHBoxLayout()

            name = QLineEdit()
            name.setPlaceholderText(f"Raum {i+1} Name")

            area = QLineEdit()
            area.setPlaceholderText("Fläche (m²)")

            height = QLineEdit()
            height.setPlaceholderText("Höhe (m)")

            usage = QComboBox()
            usage.addItems(DIN_TYPES.keys())

            row.addWidget(name)
            row.addWidget(area)
            row.addWidget(height)
            row.addWidget(usage)

            self.scroll_layout.addLayout(row)
            self.room_fields.append((name, area, height, usage))


    # Räume speichern
    def save_rooms(self):
        rooms = []

        DIN_TYPES = {
            "Wohnraum (20°C)": 20,
            "Schlafzimmer (18°C)": 18,
            "Küche (20°C)": 20,
            "Bad (24°C)": 24,
            "WC (18°C)": 18,
            "Flur (15°C)": 15,
            "Abstellraum (12°C)": 12,
            "Technikraum (10°C)": 10,
            "Keller beheizt (12°C)": 12,
            "Keller unbeheizt (10°C)": 10
        }

        for name, area, height, usage in self.room_fields:
            if name.text().strip():
                rooms.append({
                    "name": name.text(),
                    "area": float(area.text() or 0),
                    "height": float(height.text() or 0),
                    "usage": usage.currentText(),
                    "temp": DIN_TYPES[usage.currentText()]
                })

        save_rooms(rooms)


    # Heizlast berechnen
    def berechnen(self):
        self.save_rooms()

        try:
            plz = self.fields["plz"].text().strip()
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


    # Raum-Heizlast Diagramm
    def open_raum_heizlast(self):
        self.save_rooms()
        rooms = load_rooms()

        if not rooms:
            self.output.setText("❌ Keine Räume gespeichert.")
            return

        plz = self.fields["plz"].text().strip()
        nat_map = {"0": -12, "1": -12, "2": -10, "3": -12, "4": -10,
                   "5": -10, "6": -14, "7": -14, "8": -16, "9": -16}
        nat = nat_map.get(str(plz)[0], -12)

        ui = RaumHeizlastUI(nat, rooms)
        ui.show()
