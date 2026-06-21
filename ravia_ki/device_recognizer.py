import re
from dataclasses import dataclass

@dataclass
class DeviceInfo:
    hersteller: str | None = None
    serie: str | None = None
    leistung_kw: float | None = None
    kaeltemittel: str | None = None
    modellnummer: str | None = None
    typ: str | None = None


class DeviceRecognizer:
    def __init__(self):
        self._hersteller_alias = {
            "lg": "LG",
            "lg electronics": "LG",
            "therma v": "LG",
        }

        self._serien = [
            "Therma V",
        ]

        self._kaeltemittel = ["R32", "R410A", "R290"]

        self._typ_keywords = {
            "monoblock": "Monoblock",
            "split": "Split",
        }

    def parse(self, text: str) -> DeviceInfo:
        t = text.lower()

        info = DeviceInfo()

        # Hersteller
        for key, value in self._hersteller_alias.items():
            if key in t:
                info.hersteller = value
                break

        # Serie
        for serie in self._serien:
            if serie.lower() in t:
                info.serie = serie
                break

        # Leistung (z. B. 16kW, 16 kw, 16 kW)
        m_kw = re.search(r"(\d+)\s*k?w", t)
        if m_kw:
            info.leistung_kw = float(m_kw.group(1))

        # Kältemittel
        for km in self._kaeltemittel:
            if km.lower() in t:
                info.kaeltemittel = km
                break

        # Typ (Monoblock / Split)
        for key, value in self._typ_keywords.items():
            if key in t:
                info.typ = value
                break

        # Modellnummer (grob)
        m_model = re.search(r"\b[hm]\w{3,}\.\w{3,}\b", t)
        if m_model:
            info.modellnummer = m_model.group(0)

        return info
