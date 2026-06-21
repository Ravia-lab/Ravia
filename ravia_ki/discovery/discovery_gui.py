from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QMessageBox
)

from ravia_ki.discovery.web_discovery import WebDiscovery


class DiscoveryGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RaVia – Discovery Modul")
        self.setMinimumWidth(700)

        self.discovery = WebDiscovery()

        layout = QVBoxLayout()

        # Hersteller
        self.label_manufacturer = QLabel("Hersteller auswählen:")
        layout.addWidget(self.label_manufacturer)

        self.combo_manufacturer = QComboBox()
        self.combo_manufacturer.addItems(self.discovery.get_manufacturers())
        self.combo_manufacturer.currentTextChanged.connect(self.update_models)
        layout.addWidget(self.combo_manufacturer)

        # Modell / Serie
        self.label_model = QLabel("Gerät / Serie auswählen:")
        layout.addWidget(self.label_model)

        self.combo_model = QComboBox()
        self.combo_model.currentTextChanged.connect(self.update_kw)
        layout.addWidget(self.combo_model)

        # kW-Leistung
        self.label_kw = QLabel("Leistung (kW) auswählen:")
        layout.addWidget(self.label_kw)

        self.combo_kw = QComboBox()
        layout.addWidget(self.combo_kw)

        # Initiale Befüllung
        self.update_models(self.combo_manufacturer.currentText())

        # Start-Button
        self.btn_start = QPushButton("Discovery starten")
        self.btn_start.clicked.connect(self.run_discovery)
        layout.addWidget(self.btn_start)

        # Ausgabe
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def update_models(self, manufacturer):
        models = self.discovery.get_models_for_manufacturer(manufacturer)
        self.combo_model.clear()
        self.combo_model.addItems(models)
        self.update_kw()

    def update_kw(self):
        manufacturer = self.combo_manufacturer.currentText()
        model = self.combo_model.currentText()

        if not manufacturer or not model:
            return

        kw_list = self.discovery.get_kw_for_model(manufacturer, model)
        self.combo_kw.clear()
        self.combo_kw.addItems([str(k) for k in kw_list])

    def run_discovery(self):
        manufacturer = self.combo_manufacturer.currentText()
        model = self.combo_model.currentText()
        kw = self.combo_kw.currentText()

        if not manufacturer or not model or not kw:
            QMessageBox.warning(self, "Fehler", "Bitte Hersteller, Modell und kW auswählen.")
            return

        result = self.discovery.discover_device(manufacturer, model, kw)

        text = []
        text.append(f"Hersteller: {manufacturer}")
        text.append(f"Modell: {model}")
        text.append(f"Leistung: {kw} kW")
        text.append("\n--- Produktseiten ---")
        text.extend(result.product_pages)
        text.append("\n--- PDFs ---")
        text.extend(result.datasheets)
        text.append("\n--- Bilder ---")
        text.extend(result.images)
        text.append("\n--- ZIP-Dateien ---")
        text.extend(result.zip_files)

        self.output.setText("\n".join(text))


def start_discovery_gui():
    app = QApplication([])
    gui = DiscoveryGUI()
    gui.show()
    app.exec()
