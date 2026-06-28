import os
from create_plz_db import build_db

CSV = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.csv"
DB  = r"C:\Users\User\PycharmProjects\Ravia2\plz-heizlast\plz.db"

if os.path.exists(DB):
    os.remove(DB)
    print("✔ Alte DB gelöscht.")

build_db(CSV, DB)
