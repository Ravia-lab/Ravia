import os
import sys

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_best_icon_path():
    preferred = [128, 64, 48, 32, 16]
    for s in preferred:
        p = resource_path(f"icons/ravia_icon_{s}.png")
        if os.path.exists(p):
            return p
    ico = resource_path("icons/ravia_icon.ico")
    if os.path.exists(ico):
        return ico
    return None
