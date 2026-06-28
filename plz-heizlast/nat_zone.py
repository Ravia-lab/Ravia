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
