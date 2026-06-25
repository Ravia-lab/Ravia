from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QMessageBox, QComboBox, QTextEdit
)

from ravia_ki.data.rooms import load_rooms, add_room, update_room, delete_room




class RoomEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RaVia – Räume verwalten (DIN‑PRO)")

        layout = QVBoxLayout(self)

        # Raumliste
        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self.load_selected_room)
        layout.addWidget(self.list)

        # Eingabefelder
        form = QVBoxLayout()
        layout.addLayout(form)

        # Name
        self.name = QLineEdit()
        self.name.setPlaceholderText("Raumname")
        form.addWidget(self._label("Raumname"))
        form.addWidget(self.name)

        # Fläche
        self.flaeche = QLineEdit()
        self.flaeche.setPlaceholderText("Fläche m²")
        form.addWidget(self._label("Fläche (m²)"))
        form.addWidget(self.flaeche)

        # Höhe
        self.hoehe = QLineEdit()
        self.hoehe.setPlaceholderText("Höhe m")
        form.addWidget(self._label("Raumhöhe (m)"))
        form.addWidget(self.hoehe)

        # Nutzung
        self.nutzung = QComboBox()
        self.nutzung.addItems([
            "Wohnraum", "Schlafzimmer", "Bad", "Küche",
            "Flur", "Abstellraum", "Technikraum"
        ])
        self.nutzung.currentIndexChanged.connect(self.update_norm_temp)
        form.addWidget(self._label("Nutzung"))
        form.addWidget(self.nutzung)

        # Normtemperatur
        self.norm_temp = QLineEdit()
        self.norm_temp.setPlaceholderText("Normtemperatur °C")
        form.addWidget(self._label("Normtemperatur (DIN)"))
        form.addWidget(self.norm_temp)

        # Beschreibung
        self.beschreibung = QTextEdit()
        self.beschreibung.setPlaceholderText("Beschreibung / Hinweise")
        form.addWidget(self._label("Beschreibung"))
        form.addWidget(self.beschreibung)

        # Buttons
        btn_add = QPushButton("Raum speichern / aktualisieren")
        btn_add.clicked.connect(self.save_room)
        layout.addWidget(btn_add)

        btn_del = QPushButton("Raum löschen")
        btn_del.clicked.connect(self.delete_room_clicked)
        layout.addWidget(btn_del)

        self.load_rooms_into_list()

    # ---------------------------------------------------------
    # Hilfslabel
    # ---------------------------------------------------------
    def _label(self, text):
        lbl = QLabel(text)
        return lbl

    # ---------------------------------------------------------
    # Räume laden
    # ---------------------------------------------------------
    def load_rooms_into_list(self):
        self.rooms = load_rooms()
        self.list.clear()
        for r in self.rooms:
            self.list.addItem(f"{r['name']} – {r['flaeche']} m²")

    # ---------------------------------------------------------
    # Raum speichern / aktualisieren
    # ---------------------------------------------------------
    def save_room(self):
        try:
            name = self.name.text().strip()
            flaeche = float(self.flaeche.text().replace(",", "."))
            hoehe = float(self.hoehe.text().replace(",", "."))
            norm_temp = float(self.norm_temp.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte alle Werte korrekt eingeben.")
            return

        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte einen Raumnamen eingeben.")
            return

        room = {
            "name": name,
            "flaeche": flaeche,
            "hoehe": hoehe,
            "temp": norm_temp,
            "nutzung": self.nutzung.currentText(),
            "norm_temp": norm_temp,
            "beschreibung": self.beschreibung.toPlainText(),
            "aussenwaende": [],
            "fenster": [],
            "dach": [],
            "boden": [],
            "waermebruecken": [],
            "lueftung": {"typ": "Fensterlüftung", "n": 0.6}
        }

        # Prüfen ob Raum existiert → update
        selected = self.list.currentRow()
        if selected >= 0:
            old_name = self.rooms[selected]["name"]
            update_room(old_name, room)
        else:
            add_room(room)

        self.load_rooms_into_list()

    # ---------------------------------------------------------
    # Raum löschen
    # ---------------------------------------------------------
    def delete_room_clicked(self):
        item = self.list.currentItem()
        if not item:
            return
        name = item.text().split("–")[0].strip()
        delete_room(name)
        self.load_rooms_into_list()

    # ---------------------------------------------------------
    # Raum laden
    # ---------------------------------------------------------
    def load_selected_room(self):
        idx = self.list.currentRow()
        if idx < 0:
            return

        r = self.rooms[idx]

        self.name.setText(r["name"])
        self.flaeche.setText(str(r["flaeche"]))
        self.hoehe.setText(str(r["hoehe"]))
        self.nutzung.setCurrentText(r.get("nutzung", "Wohnraum"))
        self.norm_temp.setText(str(r.get("norm_temp", 20)))
        self.beschreibung.setText(r.get("beschreibung", ""))

    # ---------------------------------------------------------
    # Normtemperatur automatisch setzen
    # ---------------------------------------------------------
    def update_norm_temp(self):
        nutzung = self.nutzung.currentText()

        defaults = {
            "Wohnraum": 20,
            "Schlafzimmer": 18,
            "Bad": 24,
            "Küche": 20,
            "Flur": 15,
            "Abstellraum": 12,
            "Technikraum": 10
        }

        self.norm_temp.setText(str(defaults.get(nutzung, 20)))
