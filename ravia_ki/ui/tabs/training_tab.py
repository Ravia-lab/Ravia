from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TrainingTab(QWidget):
    """
    Minimaler Training-Tab, damit der Import funktioniert.
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Training – Modul noch nicht implementiert"))
        self.setLayout(layout)
