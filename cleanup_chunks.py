import os

for f in os.listdir("."):
    if f.startswith("project_dump_part_") and f.endswith(".txt"):
        try:
            os.remove(f)
            print("Gelöscht:", f)
        except Exception as e:
            print("Fehler:", f, e)

print("Fertig – alle Dump-Dateien gelöscht.")
