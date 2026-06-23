def is_relevant_url(url: str, keywords: list[str]) -> bool:
    url_lower = url.lower()
    return any(k.lower() in url_lower for k in keywords)


def is_relevant_pdf(url: str, keywords: list[str]) -> bool:
    url_lower = url.lower()
    return (
        url_lower.endswith(".pdf")
        and any(k.lower() in url_lower for k in keywords)
        and "manual" not in url_lower
        and "warranty" not in url_lower
    )
