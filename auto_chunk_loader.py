import os
import pyperclip

CHUNK_PREFIX = "project_dump_part_"

def load_chunks():
    files = [f for f in os.listdir(".") if f.startswith(CHUNK_PREFIX)]
    files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    return files

def main():
    chunks = load_chunks()
    print(f"{len(chunks)} Chunks gefunden.")

    for f in chunks:
        print(f"\n--- Datei: {f} ---")
        input("ENTER → Inhalt in Zwischenablage kopieren...")

        with open(f, "r", encoding="utf-8") as file:
            content = file.read()

        pyperclip.copy(content)
        print("✔ Inhalt in Zwischenablage. Jetzt hier im Chat einfügen.")

        input("ENTER → nächste Datei...")

if __name__ == "__main__":
    main()
