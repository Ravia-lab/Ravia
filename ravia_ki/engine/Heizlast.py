class Heizlast:
    """
    Heizlast-Engine nach vereinfachter DIN EN 12831.
    Kapselt alle Funktionen in einer sauberen Klasse.
    """

    def __init__(self):
        pass

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


# ============================================================
# RaVia – Heizlast nach vereinfachter DIN EN 12831
# ============================================================

# Q_T = A * U * (θ_i - θ_e)
# Q_V = 0.34 * n * V * (θ_i - θ_e)
# Q_H = (Q_T + Q_V) / 1000  → kW
# ============================================================

NAT_TABELLE = {
    "0": -12,
    "1": -12,
    "2": -10,
    "3": -12,
    "4": -10,
    "5": -10,
    "6": -14,
    "7": -14,
    "8": -16,
    "9": -16,
}


def nat_aus_plz(plz: int) -> int:
    plz_str = str(plz)
    if not plz_str:
        return -12
    return NAT_TABELLE.get(plz_str[0], -12)


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
    # 1 = schlecht, 2 = mittel, 3 = gut
    if daemmung_stufe <= 1:
        return 0.7
    elif daemmung_stufe == 2:
        return 0.6
    else:
        return 0.5


def warmwasser_leistung(personen: int) -> float:
    if personen <= 0:
        return 0.0
    return personen * 0.25  # kW


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
    """
    Vereinfachte Heizlast nach DIN EN 12831 (Gebäudeebene).
    """

    nat = nat_aus_plz(plz)
    delta_t = theta_i - nat

    u_gesamt = u_wert_aus_baujahr(baujahr)
    volumen = flaeche * raumhoehe

    # Transmission
    q_t = flaeche * u_gesamt * delta_t  # W

    # Lüftung
    n = luftwechsel_vereinfacht(daemmung_stufe)
    q_v = 0.34 * n * volumen * delta_t  # W

    # Heizlast Gebäude
    q_h = (q_t + q_v) / 1000.0  # kW

    # Warmwasser + Puffer
    q_ww = warmwasser_leistung(personen)
    q_puffer = puffer_verluste(puffer_liter)

    gesamt = q_h + q_ww + q_puffer

    return {
        "nat": nat,
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
