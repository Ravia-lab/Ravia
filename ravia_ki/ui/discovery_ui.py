import tkinter as tk
from tkinter import ttk

DEVICE_DATABASE = {
    "Daikin": {
        "Altherma 3 H HT": [8, 11, 14, 16],
        "Altherma 3 R": [4, 6, 8],
    },
    "Panasonic": {
        "Aquarea High Performance": [5, 7, 9, 12],
        "Aquarea T-CAP": [9, 12, 16],
    },
    "LG": {
        "Therma V R32": [5, 7, 9, 12],
        "Therma V Monobloc": [5, 7, 9],
    },
    "Vaillant": {
        "aroTHERM plus": [3, 5, 7, 10, 12],
    }
}


class DiscoveryUI:
    def __init__(self, root, on_start_callback):
        self.root = root
        self.on_start_callback = on_start_callback

        self.root.title("RaVia – Discovery Modul")

        # Hersteller
        ttk.Label(root, text="Hersteller auswählen:").pack(pady=5)
        self.manufacturer_var = tk.StringVar()
        self.manufacturer_dropdown = ttk.Combobox(
            root, textvariable=self.manufacturer_var,
            values=list(DEVICE_DATABASE.keys()),
            state="readonly", width=40
        )
        self.manufacturer_dropdown.pack(pady=5)
        self.manufacturer_dropdown.bind("<<ComboboxSelected>>", self.update_series)

        # Serie
        ttk.Label(root, text="Gerät / Serie auswählen:").pack(pady=5)
        self.series_var = tk.StringVar()
        self.series_dropdown = ttk.Combobox(
            root, textvariable=self.series_var,
            values=[], state="readonly", width=40
        )
        self.series_dropdown.pack(pady=5)
        self.series_dropdown.bind("<<ComboboxSelected>>", self.update_power)

        # Leistung
        ttk.Label(root, text="Leistung (kW) auswählen:").pack(pady=5)
        self.power_var = tk.StringVar()
        self.power_dropdown = ttk.Combobox(
            root, textvariable=self.power_var,
            values=[], state="readonly", width=40
        )
        self.power_dropdown.pack(pady=5)

        # Button
        ttk.Button(root, text="Discovery starten", command=self.start_discovery).pack(pady=20)

    def update_series(self, event=None):
        manufacturer = self.manufacturer_var.get()
        series_list = list(DEVICE_DATABASE[manufacturer].keys())
        self.series_dropdown["values"] = series_list
        self.series_var.set("")

    def update_power(self, event=None):
        manufacturer = self.manufacturer_var.get()
        series = self.series_var.get()
        power_list = DEVICE_DATABASE[manufacturer][series]
        self.power_dropdown["values"] = power_list
        self.power_var.set("")

    def start_discovery(self):
        manufacturer = self.manufacturer_var.get()
        series = self.series_var.get()
        power = self.power_var.get()

        self.on_start_callback(manufacturer, series, power)
