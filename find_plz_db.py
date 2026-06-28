def find_plz_db():
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    # 1️⃣ bevorzugter Ordner (DEIN echter Ordner!)
    preferred_folder = os.path.join(project_root, "plz-heizlast")
    preferred_file = os.path.join(preferred_folder, "plz.db")

    if os.path.exists(preferred_file):
        print("✔ PLZ-Datenbank (bevorzugt):", preferred_file)
        return preferred_file

    # 2️⃣ fallback: gesamte Projektsuche
    candidates = []
    for root, dirs, files in os.walk(project_root):
        for f in files:
            if f.lower().startswith("plz") and f.lower().endswith(".db"):
                full = os.path.join(root, f)
                candidates.append(full)

    if not candidates:
        print("❌ Keine PLZ-Datenbank gefunden.")
        return None

    # 3️⃣ beste Datei auswählen
    for c in candidates:
        if "plz-heizlast" in c.replace("\\", "/"):
            print("✔ PLZ-Datenbank (fallback):", c)
            return c

    # 4️⃣ letzte Rettung: erste gefundene Datei
    print("✔ PLZ-Datenbank (erste gefundene):", candidates[0])
    return candidates[0]
