from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class CopTab(QWidget):
    """
    Minimaler COP-Analyse-Tab, damit der Import funktioniert.
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("COP Analyse – Modul noch nicht implementiert"))
        self.setLayout(layout)
