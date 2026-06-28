from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class FehleranalyseTab(QWidget):
    """
    Minimaler Fehleranalyse-Tab, damit der Import funktioniert.
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Fehleranalyse – Modul noch nicht implementiert"))
        self.setLayout(layout)
