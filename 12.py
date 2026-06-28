import os

root = r"C:\Users\User\PycharmProjects\Ravia2\.venv"

for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if f.lower() == "plz.db":
            print(os.path.join(dirpath, f))
