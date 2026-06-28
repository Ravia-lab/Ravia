from PySide6.QtWidgets import QWidget, QVBoxLayout
from ravia_ki.ui.heizlast_ui import HeizlastUI

class HeizlastTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(HeizlastUI())
        self.setLayout(layout)
