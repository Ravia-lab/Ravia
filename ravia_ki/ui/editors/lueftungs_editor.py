from ravia_ki.data.rooms import save_rooms, load_rooms

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QListWidget, QMessageBox
)

from ravia_ki.data.rooms import load_rooms



class LueftungEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RaVia – Lüftung pro Raum")

        layout = QVBoxLayout(self)

        # Raumliste
        self.room_list = QListWidget()
        self.room_list.itemSelectionChanged.connect(self.load_lueftung)
        layout.addWidget(self.room_list)

        # Lüftungsart
        self.typ = QComboBox()
        self.typ.addItems([
            "Fensterlüftung",
            "Infiltration",
            "KWL ohne WRG",
            "KWL mit WRG",
            "Benutzerdefiniert"
        ])
        self.typ.currentIndexChanged.connect(self.update_default_n)
        layout.addWidget(self.typ)

        # Luftwechselrate
        self.n_edit = QLineEdit()
        self.n_edit.setPlaceholderText("Luftwechselrate n (1/h)")
        layout.addWidget(self.n_edit)

        # Speichern
        btn_save = QPushButton("Lüftung speichern")
        btn_save.clicked.connect(self.save_lueftung)
        layout.addWidget(btn_save)

        self.load_rooms()

    # ---------------------------------------------------------
    # Räume laden
    # ---------------------------------------------------------
    def load_rooms(self):
        self.rooms = load_rooms()
        self.room_list.clear()
        for r in self.rooms:
            self.room_list.addItem(r["name"])

    # ---------------------------------------------------------
    # Lüftung eines Raums anzeigen
    # ---------------------------------------------------------
    def load_lueftung(self):
        room = self.get_selected_room()
        if not room:
            return

        l = room.get("lueftung", {"typ": "Fensterlüftung", "n": 0.6})

        self.typ.setCurrentText(l.get("typ", "Fensterlüftung"))
        self.n_edit.setText(str(l.get("n", 0.6)))

    # ---------------------------------------------------------
    # Standardwerte setzen
    # ---------------------------------------------------------
    def update_default_n(self):
        typ = self.typ.currentText()

        defaults = {
            "Fensterlüftung": 0.6,
            "Infiltration": 0.8,
            "KWL ohne WRG": 0.4,
            "KWL mit WRG": 0.3,
            "Benutzerdefiniert": ""
        }

        val = defaults.get(typ, "")
        self.n_edit.setText("" if val == "" else str(val))

    # ---------------------------------------------------------
    # Lüftung speichern
    # ---------------------------------------------------------
    def save_lueftung(self):
        room = self.get_selected_room()
        if not room:
            return

        try:
            n = float(self.n_edit.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte gültige Luftwechselrate eingeben.")
            return

        room["lueftung"] = {
            "typ": self.typ.currentText(),
            "n": n
        }

        save_rooms(self.rooms)
        QMessageBox.information(self, "Gespeichert", "Lüftung erfolgreich gespeichert.")

    # ---------------------------------------------------------
    # Hilfsfunktion
    # ---------------------------------------------------------
    def get_selected_room(self):
        idx = self.room_list.currentRow()
        if idx < 0:
            return None
        return self.rooms[idx]
