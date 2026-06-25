from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QComboBox, QMessageBox
)

from ravia_ki.data.rooms import load_rooms



class BauteileEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RaVia – Bauteile (DIN‑PRO)")

        layout = QVBoxLayout(self)

        # Raumliste
        self.room_list = QListWidget()
        self.room_list.itemSelectionChanged.connect(self.load_bauteile)
        layout.addWidget(self.room_list)

        # Bauteiltyp
        self.typ = QComboBox()
        self.typ.addItems([
            "Aussenwand",
            "Innenwand unbeheizt",
            "Innenwand beheizt",
            "Dach Aussenluft",
            "Dach unbeheizt",
            "Boden Erdreich",
            "Boden Aussenluft",
            "Fenster",
            "Waermebruecke"
        ])
        self.typ.currentIndexChanged.connect(self.update_fields)
        layout.addWidget(self.typ)

        # Eingabefelder
        self.flaeche = QLineEdit()
        self.flaeche.setPlaceholderText("Fläche / Länge")
        layout.addWidget(self.flaeche)

        self.u_wert = QLineEdit()
        self.u_wert.setPlaceholderText("U-Wert / ψ-Wert")
        layout.addWidget(self.u_wert)

        self.orient = QComboBox()
        self.orient.addItems(["-", "N", "NO", "O", "SO", "S", "SW", "W", "NW"])
        layout.addWidget(self.orient)

        self.theta_u = QLineEdit()
        self.theta_u.setPlaceholderText("Temperatur unbeheizt (optional)")
        layout.addWidget(self.theta_u)

        # Fenster-spezifisch
        self.g_wert = QLineEdit()
        self.g_wert.setPlaceholderText("g-Wert (Fenster)")
        layout.addWidget(self.g_wert)

        self.rahmen = QLineEdit()
        self.rahmen.setPlaceholderText("Rahmenanteil 0–1")
        layout.addWidget(self.rahmen)

        # Buttons
        btn_add = QPushButton("Bauteil speichern")
        btn_add.clicked.connect(self.add_bauteil)
        layout.addWidget(btn_add)

        btn_del = QPushButton("Bauteil löschen")
        btn_del.clicked.connect(self.delete_bauteil)
        layout.addWidget(btn_del)

        # Bauteilliste
        self.bauteil_list = QListWidget()
        layout.addWidget(self.bauteil_list)

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
    # Bauteile anzeigen
    # ---------------------------------------------------------
    def load_bauteile(self):
        self.bauteil_list.clear()
        room = self.get_room()
        if not room:
            return

        for b in room.get("bauteile", []):
            text = f"{b['typ']} – {b.get('flaeche', b.get('laenge'))} – U/ψ={b.get('u', b.get('psi'))}"
            self.bauteil_list.addItem(text)

    # ---------------------------------------------------------
    # Felder anpassen
    # ---------------------------------------------------------
    def update_fields(self):
        typ = self.typ.currentText()

        # Fenster
        if typ == "Fenster":
            self.g_wert.setVisible(True)
            self.rahmen.setVisible(True)
            self.orient.setVisible(True)
        # Wärmebrücke
        elif typ == "Waermebruecke":
            self.g_wert.setVisible(False)
            self.rahmen.setVisible(False)
            self.orient.setVisible(False)
        # Normale Bauteile
        else:
            self.g_wert.setVisible(False)
            self.rahmen.setVisible(False)
            self.orient.setVisible(True)

    # ---------------------------------------------------------
    # Bauteil speichern
    # ---------------------------------------------------------
    def add_bauteil(self):
        room = self.get_room()
        if not room:
            return

        typ = self.typ.currentText()

        try:
            fl = float(self.flaeche.text().replace(",", "."))
            u = float(self.u_wert.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte Fläche/Länge und U/ψ korrekt eingeben.")
            return

        bauteil = {"typ": typ}

        if typ == "Waermebruecke":
            bauteil["psi"] = u
            bauteil["laenge"] = fl
        else:
            bauteil["flaeche"] = fl
            bauteil["u"] = u
            bauteil["orient"] = self.orient.currentText()

            if self.theta_u.text():
                bauteil["theta_u"] = float(self.theta_u.text().replace(",", "."))

            if typ == "Fenster":
                bauteil["g"] = float(self.g_wert.text().replace(",", "."))
                bauteil["rahmen"] = float(self.rahmen.text().replace(",", "."))

        room.setdefault("bauteile", []).append(bauteil)
        save_rooms(self.rooms)
        self.load_bauteile()

    # ---------------------------------------------------------
    # Bauteil löschen
    # ---------------------------------------------------------
    def delete_bauteil(self):
        room = self.get_room()
        if not room:
            return

        idx = self.bauteil_list.currentRow()
        if idx < 0:
            return

        del room["bauteile"][idx]
        save_rooms(self.rooms)
        self.load_bauteile()

    # ---------------------------------------------------------
    # Hilfsfunktion
    # ---------------------------------------------------------
    def get_room(self):
        idx = self.room_list.currentRow()
        if idx < 0:
            return None
        return self.rooms[idx]
