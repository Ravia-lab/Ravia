from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QComboBox, QMessageBox
)

from material_bib import MATERIAL_BIB


class SchichtEditor(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.setWindowTitle("RaVia – Schichtaufbau (U-Wert Berechnung)")
        self.callback = callback  # Rückgabe an Bauteile-Editor

        layout = QVBoxLayout(self)

        # Materialauswahl
        self.material = QComboBox()
        self.material.addItems(MATERIAL_BIB.keys())
        layout.addWidget(self.material)

        # Dicke
        self.dicke = QLineEdit()
        self.dicke.setPlaceholderText("Dicke in m (z.B. 0.24)")
        layout.addWidget(self.dicke)

        # Schichtenliste
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Buttons
        btn_add = QPushButton("Schicht hinzufügen")
        btn_add.clicked.connect(self.add_layer)
        layout.addWidget(btn_add)

        btn_del = QPushButton("Schicht löschen")
        btn_del.clicked.connect(self.delete_layer)
        layout.addWidget(btn_del)

        btn_calc = QPushButton("U-Wert berechnen")
        btn_calc.clicked.connect(self.calculate_u)
        layout.addWidget(btn_calc)

        self.layers = []

    def add_layer(self):
        try:
            d = float(self.dicke.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte gültige Dicke eingeben.")
            return

        mat = self.material.currentText()
        lam = MATERIAL_BIB[mat]

        layer = {"material": mat, "dicke": d, "lambda": lam}
        self.layers.append(layer)

        self.list.addItem(f"{mat} – {d} m – λ={lam}")

    def delete_layer(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        del self.layers[idx]
        self.list.takeItem(idx)

    def calculate_u(self):
        if not self.layers:
            QMessageBox.warning(self, "Fehler", "Keine Schichten vorhanden.")
            return

        r_total = 0.13  # Innenoberfläche

        for l in self.layers:
            r_total += l["dicke"] / l["lambda"]

        r_total += 0.04  # Außenoberfläche

        u = 1 / r_total

        QMessageBox.information(self, "U-Wert", f"U-Wert = {round(u, 3)} W/m²K")

        # Rückgabe an Bauteile-Editor
        self.callback(round(u, 3))
        self.close()
