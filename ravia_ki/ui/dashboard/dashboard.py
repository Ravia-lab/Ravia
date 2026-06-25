from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QFrame, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ravia_ki.ui.tabs.heizlast_tab import HeizlastTab
from ravia_ki.utils.icons import get_best_icon_path


class RaViaDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RaVia – AI HVAC Intelligence")
        self.setMinimumSize(1400, 900)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)

        logo_label = QLabel()
        icon_path = get_best_icon_path()
        if icon_path:
            pixmap = QPixmap(icon_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)

        title = QLabel("RaVia – AI HVAC Intelligence")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00E5E5;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(HeizlastTab(), "Heizlast")
        self.tabs.addTab(QWidget(), "Auslegung")
        self.tabs.addTab(QWidget(), "COP Analyse")
        self.tabs.addTab(QWidget(), "Fehleranalyse")
        self.tabs.addTab(QWidget(), "Simulation")
        self.tabs.addTab(QWidget(), "Training")

        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)

        self.setCentralWidget(main_widget)
