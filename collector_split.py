import os

OUTPUT_PREFIX = "project_dump_part_"
MAX_SIZE = 80 * 1024  # 80 KB pro Datei (Chat-sicher)
EXTENSIONS = [".py", ".json", ".txt"]


def write_chunk(chunks, index, buffer):
    filename = f"{OUTPUT_PREFIX}{index}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(buffer)
    chunks.append(filename)


def collect_files(root="."):
    chunks = []
    buffer = ""
    index = 1

    for folder, _, files in os.walk(root):
        folder_header = f"\n\n=== FOLDER: {folder} ===\n"

        if len(buffer) + len(folder_header) > MAX_SIZE:
            write_chunk(chunks, index, buffer)
            index += 1
            buffer = ""

        buffer += folder_header

        for file in files:
            path = os.path.join(folder, file)
            ext = os.path.splitext(file)[1].lower()

            if ext in EXTENSIONS:
                header = f"\n--- FILE: {path} ---\n"

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"[UNABLE TO READ FILE: {e}]\n"

                block = header + content

                if len(block) > MAX_SIZE:
                    start = 0
                    while start < len(block):
                        part = block[start:start + MAX_SIZE]
                        write_chunk(chunks, index, part)
                        index += 1
                        start += MAX_SIZE
                    continue

                if len(buffer) + len(block) > MAX_SIZE:
                    write_chunk(chunks, index, buffer)
                    index += 1
                    buffer = ""

                buffer += block

            elif ext == ".db":
                block = f"\n--- DATABASE FILE (name only): {path} ---\n"

                if len(buffer) + len(block) > MAX_SIZE:
                    write_chunk(chunks, index, buffer)
                    index += 1
                    buffer = ""

                buffer += block

    if buffer:
        write_chunk(chunks, index, buffer)

    print("Fertig! Dateien erzeugt:")
    for c in chunks:
        print(" →", c)


if __name__ == "__main__":
    collect_files()
