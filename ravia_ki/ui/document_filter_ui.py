import tkinter as tk
from tkinter import ttk

class DocumentFilterUI:
    def __init__(self, root, pdf_list):
        self.root = root
        self.pdf_list = pdf_list

        self.root.title("RaVia Dokumentenfilter")

        # Kategorien aus der Engine extrahieren
        self.categories = sorted(list({pdf["category"] for pdf in pdf_list}))
        self.categories.insert(0, "alle")

        # Dropdown
        self.selected_category = tk.StringVar(value="alle")
        ttk.Label(root, text="Dokumenttyp auswählen:").pack(pady=5)

        self.dropdown = ttk.Combobox(
            root,
            textvariable=self.selected_category,
            values=self.categories,
            state="readonly",
            width=40
        )
        self.dropdown.pack(pady=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.update_list)

        # Liste
        self.listbox = tk.Listbox(root, width=120, height=25)
        self.listbox.pack(pady=10)

        self.update_list()

    def update_list(self, event=None):
        """Filtert die Liste nach Kategorie."""
        self.listbox.delete(0, tk.END)
        selected = self.selected_category.get()

        for pdf in self.pdf_list:
            if selected == "alle" or pdf["category"] == selected:
                self.listbox.insert(tk.END, f"[{pdf['category']}]  {pdf['url']}")
