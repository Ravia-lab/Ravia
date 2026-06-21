ALLOWED_DOMAINS = [
    "lg.com", "panasonic", "vaillant", "daikin", "wolf", "viessmann",
    "mitsubishi", "stiebel", "bosch", "nibe"
]

def is_relevant_domain(url: str) -> bool:
    url_l = url.lower()
    return any(domain in url_l for domain in ALLOWED_DOMAINS)

def is_probably_pdf(url: str) -> bool:
    return ".pdf" in url.lower().split("?")[0]
