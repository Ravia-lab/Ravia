import asyncio
from urllib.parse import urljoin

from ravia_ki.discovery.manufacturer_profiles import MANUFACTURERS
from ravia_ki.discovery.human_browser import HumanBrowser


class HumanDiscoveryEngine:
    async def discover(self, manufacturer_key, series=None, power=None):
        profile = MANUFACTURERS.get(manufacturer_key.lower())
        if not profile:
            return {"error": f"Herstellerprofil nicht gefunden: {manufacturer_key}"}

        seeds = profile["seeds"]
        keywords = profile["product_keywords"]

        browser = HumanBrowser()
        await browser.start()

        all_links = []

        for seed in seeds:
            await browser.goto(seed)
            links = await browser.get_links()
            full_links = [l if l.startswith("http") else urljoin(seed, l) for l in links]
            all_links.extend(full_links)

            # kleine Pause zwischen Seeds, um Bot-Trigger zu vermeiden
            await asyncio.sleep(2.0 + 3.0 * (len(seeds) > 1))

        await browser.close()

        product_pages = [
            u for u in all_links
            if any(k.lower() in u.lower() for k in keywords)
        ]
        pdfs = [u for u in all_links if u.lower().endswith(".pdf")]

        return {
            "manufacturer": profile["name"],
            "series": series,
            "power": power,
            "product_pages": sorted(set(product_pages)),
            "pdfs": sorted(set(pdfs)),
            "count_pages": len(set(product_pages)),
            "count_pdfs": len(set(pdfs)),
        }
