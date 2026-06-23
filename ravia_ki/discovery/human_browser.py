import asyncio
import random
from playwright.async_api import async_playwright


class HumanBrowser:
    def __init__(self):
        self.play = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        self.play = await async_playwright().start()
        self.browser = await self.play.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        )
        self.context = await self.browser.new_context(
            user_agent=self._random_user_agent(),
            viewport=self._random_viewport(),
        )
        self.page = await self.context.new_page()

    async def goto(self, url):
        await self.page.goto(url, timeout=60000, wait_until="networkidle")
        await asyncio.sleep(random.uniform(1.0, 3.0))  # „Lesepause“
        await self._handle_cookie_banner()
        await self._human_scroll()
        await self._human_mouse_move()

    async def get_links(self):
        anchors = await self.page.query_selector_all("a")
        urls = []
        for a in anchors:
            href = await a.get_attribute("href")
            if href:
                urls.append(href)
        return urls

    async def close(self):
        if self.context:
            await self.context.storage_state(path="human_session_state.json")
        if self.browser:
            await self.browser.close()
        if self.play:
            await self.play.stop()

    async def _handle_cookie_banner(self):
        # einfache, generische Cookie-Buttons
        selectors = [
            "text=Accept all",
            "text=Accept All",
            "text=Akzeptieren",
            "text=Alle akzeptieren",
            "button:has-text('Accept')",
        ]
        for sel in selectors:
            try:
                el = self.page.locator(sel)
                if await el.count() > 0:
                    await asyncio.sleep(random.uniform(0.8, 2.0))
                    await el.first.click()
                    await asyncio.sleep(random.uniform(0.8, 2.0))
                    break
            except:
                continue

    async def _human_scroll(self):
        # Mischung aus kleinen und größeren Scrolls, inkl. Pausen
        steps = random.randint(4, 10)
        for _ in range(steps):
            delta = random.randint(200, 900)
            await self.page.mouse.wheel(0, delta)
            await asyncio.sleep(random.uniform(0.3, 1.0))
        # manchmal leicht zurückscrollen
        if random.random() < 0.4:
            await self.page.mouse.wheel(0, -random.randint(200, 600))
            await asyncio.sleep(random.uniform(0.4, 1.2))

    async def _human_mouse_move(self):
        # unregelmäßige, leicht „zittrige“ Mausbewegungen
        for _ in range(random.randint(8, 20)):
            x = random.randint(50, 1250)
            y = random.randint(50, 700)
            steps = random.randint(5, 25)
            await self.page.mouse.move(x, y, steps=steps)
            await asyncio.sleep(random.uniform(0.05, 0.25))

    def _random_user_agent(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        ]
        return random.choice(agents)

    def _random_viewport(self):
        widths = [1280, 1366, 1440, 1536]
        heights = [720, 768, 800, 900]
        return {"width": random.choice(widths), "height": random.choice(heights)}
