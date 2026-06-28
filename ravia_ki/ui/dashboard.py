import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTabWidget
)

# ---------------------------------------------------------
#   IMPORTS DER TABS
# ---------------------------------------------------------

from ravia_ki.ui.tabs.heizlast_tab import HeizlastTab
from ravia_ki.ui.tabs.auslegung_tab import AuslegungTab
from ravia_ki.ui.tabs.cop_tab import CopTab
from ravia_ki.ui.tabs.fehleranalyse_tab import FehleranalyseTab
from ravia_ki.ui.tabs.simulation_tab import SimulationTab
from ravia_ki.ui.tabs.training_tab import TrainingTab


# ---------------------------------------------------------
#   DASHBOARD-KLASSE
# ---------------------------------------------------------

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RaVia – AI HVAC Intelligence")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(800)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # ---------------------------------------------------------
        #   TABS HINZUFÜGEN
        # ---------------------------------------------------------

        self.tabs.addTab(HeizlastTab(), "Heizlast")
        self.tabs.addTab(AuslegungTab(), "Auslegung")
        self.tabs.addTab(CopTab(), "COP Analyse")
        self.tabs.addTab(FehleranalyseTab(), "Fehleranalyse")
        self.tabs.addTab(SimulationTab(), "Simulation")
        self.tabs.addTab(TrainingTab(), "Training")

        layout.addWidget(self.tabs)
        self.setLayout(layout)


# ---------------------------------------------------------
#   STARTBLOCK – WICHTIG!
# ---------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RaViaDashboard()
    window.show()
    sys.exit(app.exec())
