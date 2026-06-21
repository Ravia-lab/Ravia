from rooms import load_rooms


def delta_t(nat: float, innen_temp: float) -> float:
    return innen_temp - nat


def q_transmission(flaeche: float, u: float, dt: float) -> float:
    """Transmission: Q_T = A * U * ΔT (W)"""
    return flaeche * u * dt



def q_lueftung(n: float, volumen: float, dt: float) -> float:
    return 0.34 * n * volumen * dt


def q_waermebruecke(psi: float, laenge: float, dt: float) -> float:
    return psi * laenge * dt


def berechne_raum_heizlast(raum: dict, nat: float) -> dict:
    innen_temp = float(raum.get("norm_temp", raum.get("temp", 20.0)))
    dt = delta_t(nat, innen_temp)

    volumen = raum["flaeche"] * raum["hoehe"]

    q_t = 0.0
    q_v = 0.0
    q_psi = 0.0

    bauteile = raum.get("bauteile", [])

    for b in bauteile:
        typ = b.get("typ", "")
        if typ == "Waermebruecke":
            psi = float(b["psi"])
            laenge = float(b["laenge"])
            q_psi += q_waermebruecke(psi, laenge, dt)
        else:
            fla = float(b["flaeche"])
            u = float(b["u"])
            # hier könnte man je nach Randbed. noch differenzieren
            q_t += q_transmission(fla, u, dt)

    lueftung = raum.get("lueftung", {"n": 0.6})
    n = float(lueftung.get("n", 0.6))
    q_v = q_lueftung(n, volumen, dt)

    q_sum_w = q_t + q_v + q_psi
    q_sum_w *= 1.10  # 10 % Zuschlag

    return {
        "raum": raum["name"],
        "q_t": round(q_t, 1),
        "q_v": round(q_v, 1),
        "q_psi": round(q_psi, 1),
        "q_sum": round(q_sum_w / 1000, 3),  # kW
    }


def berechne_gebaeude_heizlast(nat: float) -> dict:
    rooms = load_rooms()
    ergebnisse = []
    gesamt_kw = 0.0

    for r in rooms:
        res = berechne_raum_heizlast(r, nat)
        ergebnisse.append(res)
        gesamt_kw += res["q_sum"]

    return {
        "raeume": ergebnisse,
        "gesamt_kw": round(gesamt_kw, 3)
    }
