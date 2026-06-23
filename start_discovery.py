from ravia_ki.ui.discovery_ui import DiscoveryUI
import tkinter as tk

def main():
    root = tk.Tk()
    DiscoveryUI(root, lambda *args: print("Discovery gestartet:", args))
    root.mainloop()

if __name__ == "__main__":
    main()
