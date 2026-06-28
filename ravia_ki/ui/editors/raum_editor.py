from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QScrollArea
)
from ravia_ki.data.rooms import load_rooms, save_rooms


class RoomEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Räume verwalten")
        self.resize(500, 600)

        self.rooms = load_rooms()

        main_layout = QVBoxLayout(self)

        # Anzahl der Räume
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Anzahl Räume:"))
        self.count_input = QLineEdit()
        count_layout.addWidget(self.count_input)

        self.generate_btn = QPushButton("Eingabefelder erzeugen")
        self.generate_btn.clicked.connect(self.generate_fields)

        main_layout.addLayout(count_layout)
        main_layout.addWidget(self.generate_btn)

        # Scrollbereich für dynamische Felder
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidget(self.scroll_widget)

        main_layout.addWidget(self.scroll)

        # Speichern
        self.save_btn = QPushButton("Räume speichern")
        self.save_btn.clicked.connect(self.save_rooms)
        main_layout.addWidget(self.save_btn)

        # Wenn Räume existieren → anzeigen
        if self.rooms:
            self.generate_fields_from_existing()

    def generate_fields(self):
        """Erzeugt Eingabefelder basierend auf der Anzahl."""
        try:
            count = int(self.count_input.text())
        except:
            return

        # Alte Felder löschen
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.room_fields = []

        for i in range(count):
            row = QHBoxLayout()
            name = QLineEdit()
            name.setPlaceholderText(f"Raum {i+1} Name")

            area = QLineEdit()
            area.setPlaceholderText("Fläche (m²)")

            height = QLineEdit()
            height.setPlaceholderText("Höhe (m)")

            row.addWidget(name)
            row.addWidget(area)
            row.addWidget(height)

            self.scroll_layout.addLayout(row)
            self.room_fields.append((name, area, height))

    def generate_fields_from_existing(self):
        """Erzeugt Felder aus gespeicherten Räumen."""
        self.room_fields = []

        for r in self.rooms:
            row = QHBoxLayout()

            name = QLineEdit(r.get("name", ""))
            area = QLineEdit(str(r.get("area", "")))
            height = QLineEdit(str(r.get("height", "")))

            row.addWidget(name)
            row.addWidget(area)
            row.addWidget(height)

            self.scroll_layout.addLayout(row)
            self.room_fields.append((name, area, height))

    def save_rooms(self):
        """Speichert alle Räume."""
        rooms = []

        for name, area, height in self.room_fields:
            if name.text().strip():
                rooms.append({
                    "name": name.text(),
                    "area": float(area.text() or 0),
                    "height": float(height.text() or 0)
                })

        save_rooms(rooms)
        self.close()
