from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AuslegungTab(QWidget):
    """
    Minimaler Auslegung-Tab, damit der Import funktioniert.
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Auslegung – Modul noch nicht implementiert"))
        self.setLayout(layout)
