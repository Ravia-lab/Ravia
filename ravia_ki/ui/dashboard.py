from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout
from ravia_ki.ui.tabs.heizlast_tab import HeizlastTab


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RaVia – Dashboard")
        self.resize(1400, 900)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tabs hinzufügen
        self.tabs.addTab(HeizlastTab(), "Heizlast")
        # Weitere Tabs folgen später


if __name__ == "__main__":
    app = QApplication([])
    window = Dashboard()
    window.show()
    app.exec()
