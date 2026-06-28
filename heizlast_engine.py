import sqlite3

DB_FILE = "plz.db"

def get_plz_info(plz: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    row = cur.execute(
        "SELECT plz, bundesland, kreis, typ FROM plz WHERE plz = ?",
        (str(plz),)
    ).fetchone()
    conn.close()

    if not row:
        raise ValueError(f"PLZ {plz} nicht in plz.db gefunden.")

    return {
        "plz": row[0],
        "bundesland": row[1],
        "kreis": row[2],
        "typ": row[3],
    }

NAT_ZONES = {
    "Sachsen": 2,
    "Thüringen": 2,
    "Bayern": 2,
    "Baden-Württemberg": 3,
    "Hessen": 3,
    "Rheinland-Pfalz": 3,
    "Saarland": 3,
    "Sachsen-Anhalt": 3,
    "Niedersachsen": 4,
    "NRW": 4,
    "Nordrhein-Westfalen": 4,
    "Berlin": 4,
    "Brandenburg": 4,
    "Hamburg": 5,
    "Bremen": 5,
    "Schleswig-Holstein": 5
}

AUSLEGUNG = {
    1: -16,
    2: -14,
    3: -12,
    4: -10,
    5: -8,
    6: -6
}

def nat_aus_bundesland(bundesland: str) -> int:
    return NAT_ZONES.get(bundesland, 4)

def auslegung_temp(nat_zone: int) -> float:
    return AUSLEGUNG[nat_zone]

def u_wert_aus_baujahr(baujahr: int) -> float:
    if baujahr < 1978:
        return 1.6
    elif baujahr < 1995:
        return 1.3
    elif baujahr < 2005:
        return 1.0
    else:
        return 0.8

def luftwechsel_vereinfacht(daemmung_stufe: int) -> float:
    if daemmung_stufe <= 1:
        return 0.7
    elif daemmung_stufe == 2:
        return 0.6
    else:
        return 0.5

def warmwasser_leistung(personen: int) -> float:
    if personen <= 0:
        return 0.0
    return personen * 0.25

def puffer_verluste(puffer_liter: int) -> float:
    if puffer_liter <= 0:
        return 0.0
    return round(puffer_liter * 0.02 / 100.0, 2)

def berechne_heizlast_din(
    plz: int,
    flaeche: float,
    raumhoehe: float,
    baujahr: int,
    daemmung_stufe: int,
    personen: int,
    puffer_liter: int,
    theta_i: float = 20.0,
):
    plz_info = get_plz_info(plz)
    bundesland = plz_info["bundesland"]

    nat_zone = nat_aus_bundesland(bundesland)
    theta_e = auslegung_temp(nat_zone)

    delta_t = theta_i - theta_e
    u_gesamt = u_wert_aus_baujahr(baujahr)
    volumen = flaeche * raumhoehe

    q_t = flaeche * u_gesamt * delta_t
    n = luftwechsel_vereinfacht(daemmung_stufe)
    q_v = 0.34 * n * volumen * delta_t

    q_h = (q_t + q_v) / 1000.0
    q_ww = warmwasser_leistung(personen)
    q_puffer = puffer_verluste(puffer_liter)

    gesamt = q_h + q_ww + q_puffer

    return {
        "plz": plz,
        "bundesland": bundesland,
        "nat_zone": nat_zone,
        "theta_e": theta_e,
        "delta_t": delta_t,
        "u_gesamt": round(u_gesamt, 3),
        "luftwechsel": n,
        "q_t": round(q_t, 1),
        "q_v": round(q_v, 1),
        "heizlast_geb": round(q_h, 2),
        "warmwasser": round(q_ww, 2),
        "puffer": round(q_puffer, 2),
        "gesamt": round(gesamt, 2),
    }

class Heizlast:
    def berechnen(
        self,
        plz: int,
        flaeche: float,
        raumhoehe: float,
        baujahr: int,
        daemmung_stufe: int,
        personen: int,
        puffer_liter: int,
        theta_i: float = 20.0,
    ):
        return berechne_heizlast_din(
            plz,
            flaeche,
            raumhoehe,
            baujahr,
            daemmung_stufe,
            personen,
            puffer_liter,
            theta_i,
        )
