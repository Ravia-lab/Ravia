from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SimulationTab(QWidget):
    """
    Minimaler Simulation-Tab, damit der Import funktioniert.
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Simulation – Modul noch nicht implementiert"))
        self.setLayout(layout)
