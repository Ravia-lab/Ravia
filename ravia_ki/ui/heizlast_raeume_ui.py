from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
import os

from ravia_ki.engine.din_engine import berechne_gebaeude_heizlast


class RaumHeizlastUI(QWidget):
    def __init__(self, nat):
        super().__init__()
        self.setWindowTitle("RaVia – Raumweise Heizlast (DIN EN 12831)")

        layout = QVBoxLayout(self)

        # Ergebnisliste
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Diagramm
        self.diagram_label = QLabel()
        self.diagram_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.diagram_label)

        # Gesamtheizlast
        self.sum_label = QLabel()
        self.sum_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sum_label)

        # Berechnung durchführen
        self.load_results(nat)

    def load_results(self, nat):
        result = berechne_gebaeude_heizlast(nat)

        self.list.clear()
        raum_namen = []
        raum_kw = []

        for r in result["raeume"]:
            text = (
                f"{r['raum']}: "
                f"Qₜ={r['q_t']} W, "
                f"Qᵥ={r['q_v']} W, "
                f"Qψ={r['q_psi']} W → "
                f"{r['q_sum']} kW"
            )
            self.list.addItem(text)

            raum_namen.append(r["raum"])
            raum_kw.append(r["q_sum"])

        # Diagramm erzeugen
        self.create_chart(raum_namen, raum_kw)

        self.sum_label.setText(
            f"<b>Gesamt-Heizlast Gebäude:</b> {result['gesamt_kw']} kW"
        )

    def create_chart(self, labels, values):
        plt.figure(figsize=(6, 4))
        plt.bar(labels, values, color="#00E5E5")
        plt.title("Heizlast pro Raum (kW)")
        plt.ylabel("kW")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        chart_path = "raum_heizlast.png"
        plt.savefig(chart_path, dpi=120)
        plt.close()

        if os.path.exists(chart_path):
            pixmap = QPixmap(chart_path)
            self.diagram_label.setPixmap(pixmap)
