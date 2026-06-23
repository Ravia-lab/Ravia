LG_PROFILE = {
    "name": "LG",
    "seeds": [
        "https://www.lg.com/global/business/air-solution",
        "https://www.lg.com/global/business/air-solution/air-to-water-heat-pump",
    ],
    "product_keywords": ["product", "air", "solution", "heat", "pump"],
    "pdf_keywords": ["manual", "document", "datasheet", "spec", "pdf"],
    "scroll": True,
    "click_download_tab": True,
}

PANASONIC_PROFILE = {
    "name": "Panasonic",
    "seeds": [
        "https://www.panasonic.com/global/business/psna/air-conditioning.html",
    ],
    "product_keywords": ["product", "aquarea", "heat", "pump"],
    "pdf_keywords": ["manual", "datasheet", "brochure", "pdf"],
    "scroll": True,
    "click_download_tab": True,
}

DAIKIN_PROFILE = {
    "name": "Daikin",
    "seeds": [
        "https://www.daikin.eu/en_us/products.html",
    ],
    "product_keywords": ["product", "heat", "pump", "altherma"],
    "pdf_keywords": ["manual", "installation", "datasheet", "pdf"],
    "scroll": False,
    "click_download_tab": False,
}

VAILLANT_PROFILE = {
    "name": "Vaillant",
    "seeds": [
        "https://www.vaillant.de/produkte/",
    ],
    "product_keywords": ["produkt", "produktdetail", "aro", "therm"],
    "pdf_keywords": ["datenblatt", "bedienungsanleitung", "montage", "pdf"],
    "scroll": False,
    "click_download_tab": True,
}

MANUFACTURERS = {
    "lg": LG_PROFILE,
    "panasonic": PANASONIC_PROFILE,
    "daikin": DAIKIN_PROFILE,
    "vaillant": VAILLANT_PROFILE,
}
