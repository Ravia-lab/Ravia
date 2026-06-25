import os

FILES_NEEDED = [
    "main.py",
    "Heizlast.py",
    "din_engine.py",
    "raum_editor.py",
    "bauteile_editor.py",
    "lueftungs_editor.py",
    "heizlast_raeume_ui.py",
    "rooms.py",
    "rooms.json",
]

FOLDERS_NEEDED = [
    "ravia_ki/ui",
]

MAX_SIZE = 80 * 1024
OUTPUT_PREFIX = "dashboard_dump_"


def safe_read(path):
    try:
        return open(path, "r", encoding="utf-8").read()
    except:
        try:
            return open(path, "r", encoding="latin-1").read()
        except Exception as e:
            return f"[UNABLE TO READ FILE: {e}]"


def write_chunk(index, buffer):
    filename = f"{OUTPUT_PREFIX}{index}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(buffer)
    print(" → Chunk erzeugt:", filename)
    return filename


def collect():
    print("Starte Splitter…")
    print("Arbeitsverzeichnis:", os.getcwd())

    chunks = []
    buffer = ""
    index = 1

    print("\n=== Einzeldateien ===")
    for file in FILES_NEEDED:
        print("Prüfe:", file)
        if not os.path.exists(file):
            print("  ❌ existiert nicht")
            continue

        print("  ✔ wird verarbeitet")

        header = f"\n\n=== FILE: {file} ===\n"
        content = safe_read(file)
        block = header + content

        if len(block) > MAX_SIZE:
            print("  ⚠ Datei wird gesplittet")
            start = 0
            while start < len(block):
                part = block[start:start + MAX_SIZE]
                write_chunk(index, part)
                index += 1
                start += MAX_SIZE
            continue

        if len(buffer) + len(block) > MAX_SIZE:
            write_chunk(index, buffer)
            index += 1
            buffer = ""

        buffer += block

    print("\n=== UI-Ordner ===")
    for folder in FOLDERS_NEEDED:
        print("Prüfe Ordner:", folder)
        if not os.path.exists(folder):
            print("  ❌ existiert nicht")
            continue

        for root, _, files in os.walk(folder):
            for file in files:
                path = os.path.join(root, file)
                print("  ✔ Datei:", path)

                header = f"\n\n=== FILE: {path} ===\n"
                content = safe_read(path)
                block = header + content

                if len(block) > MAX_SIZE:
                    print("  ⚠ Datei wird gesplittet")
                    start = 0
                    while start < len(block):
                        part = block[start:start + MAX_SIZE]
                        write_chunk(index, part)
                        index += 1
                        start += MAX_SIZE
                    continue

                if len(buffer) + len(block) > MAX_SIZE:
                    write_chunk(index, buffer)
                    index += 1
                    buffer = ""

                buffer += block

    if buffer:
        write_chunk(index, buffer)

    print("\nFertig.")
    input("ENTER zum Beenden…")


if __name__ == "__main__":
    collect()
