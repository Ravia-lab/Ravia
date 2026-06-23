import tkinter as tk
from tkinter import ttk

from ravia_ki.discovery.manufacturer_profiles import MANUFACTURERS

# Deine echte Geräte-Datenbank
from ravia_ki.database.device_database import DEVICE_DATABASE



class DiscoveryUI:
    def __init__(self, root, on_start_callback=None):
        self.root = root
        self.on_start_callback = on_start_callback

        self.root.title("RaVia – Discovery Modul")

        # Hersteller-Namen aus MANUFACTURERS
        self.manufacturer_keys = list(MANUFACTURERS.keys())
        self.manufacturer_names = [MANUFACTURERS[k]["name"] for k in self.manufacturer_keys]

        # Hersteller
        ttk.Label(root, text="Hersteller auswählen:").pack(pady=5)
        self.manufacturer_var = tk.StringVar()
        self.manufacturer_dropdown = ttk.Combobox(
            root, textvariable=self.manufacturer_var,
            values=self.manufacturer_names,
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

    def get_key_from_name(self, name):
        for k in self.manufacturer_keys:
            if MANUFACTURERS[k]["name"] == name:
                return k
        return None

    def update_series(self, event=None):
        manu_name = self.manufacturer_var.get()

        # Serien aus DEVICE_DATABASE
        if manu_name in DEVICE_DATABASE:
            series_list = list(DEVICE_DATABASE[manu_name].keys())
        else:
            series_list = ["Keine Serien gefunden"]

        self.series_dropdown["values"] = series_list
        self.series_var.set("")

        # Leistung zurücksetzen
        self.power_dropdown["values"] = []
        self.power_var.set("")

    def update_power(self, event=None):
        manu_name = self.manufacturer_var.get()
        series = self.series_var.get()

        if manu_name in DEVICE_DATABASE and series in DEVICE_DATABASE[manu_name]:
            power_list = DEVICE_DATABASE[manu_name][series]
        else:
            power_list = []

        self.power_dropdown["values"] = power_list
        self.power_var.set("")

    def start_discovery(self):
        manu_name = self.manufacturer_var.get()
        series = self.series_var.get()
        power = self.power_var.get()

        if self.on_start_callback:
            self.on_start_callback(manu_name, series, power)
