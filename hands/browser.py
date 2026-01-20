"""
Jephthah Browser Controller
Human-like browser automation with Playwright
"""

import asyncio
import random
import time
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle
from loguru import logger

from config.settings import config, DATA_DIR


class BrowserController:
    """Human-like browser automation"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.user_data_dir = DATA_DIR / "browser_profile"
        self._is_initialized = False
        
    async def initialize(self, headless: bool = True):
        """Initialize the browser"""
        if self._is_initialized:
            return
            
        self.playwright = await async_playwright().start()
        
        # Use persistent context to maintain cookies/sessions
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--hide-scrollbars',
                '--mute-audio',
                '--ignore-certificate-errors',  # Helpful for some proxies/sites
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-GB', # Match VPS location or target audience
            timezone_id='Europe/London',
            permissions=['geolocation'],
            geolocation={'latitude': 51.5074, 'longitude': -0.1278}, # London coordinates
            extra_http_headers={
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-GB', 'en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = {runtime: {}};
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        self.page = await self.context.new_page()
        self._is_initialized = True
        logger.info("Browser initialized")
    
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._is_initialized = False
        logger.info("Browser closed")
    
    # === NAVIGATION ===
    
    async def goto(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """Navigate to a URL"""
        try:
            await self._human_delay(500, 1500)
            response = await self.page.goto(url, wait_until=wait_until, timeout=30000)
            await self._human_delay(1000, 2000)
            logger.info(f"Navigated to: {url}")
            return response.ok if response else False
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url
    
    async def get_page_title(self) -> str:
        """Get current page title"""
        return await self.page.title()
    
    async def get_page_content(self) -> str:
        """Get page HTML content"""
        return await self.page.content()
    
    async def get_page_text(self) -> str:
        """Get all visible text on page"""
        return await self.page.inner_text('body')
    
    # === HUMAN-LIKE TYPING ===
    
    async def type_like_human(self, selector: str, text: str, clear_first: bool = True):
        """Type text with human-like delays"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            
            if clear_first:
                await element.click()
                await self.page.keyboard.press('Control+A')
                await self._human_delay(100, 200)
                await self.page.keyboard.press('Backspace')
            
            for char in text:
                await element.type(char, delay=random.randint(50, 150))
                
                # Occasional pause like thinking
                if random.random() < 0.1:
                    await self._human_delay(200, 500)
            
            logger.debug(f"Typed into {selector}")
            return True
        except Exception as e:
            logger.error(f"Type error: {e}")
            return False
    
    # === CLICKING ===
    
    async def click_like_human(self, selector: str) -> bool:
        """Click with human-like behavior"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            
            # Move mouse to element with bezier curve (simplified)
            box = await element.bounding_box()
            if box:
                target_x = box['x'] + box['width'] / 2 + random.randint(-5, 5)
                target_y = box['y'] + box['height'] / 2 + random.randint(-3, 3)
                
                await self.page.mouse.move(target_x, target_y, steps=random.randint(10, 25))
                await self._human_delay(100, 300)
            
            await element.click()
            await self._human_delay(200, 500)
            logger.debug(f"Clicked: {selector}")
            return True
        except Exception as e:
            logger.error(f"Click error: {e}")
            return False
    
    async def click_text(self, text: str) -> bool:
        """Click element containing specific text"""
        try:
            await self.page.click(f"text={text}")
            await self._human_delay(200, 500)
            return True
        except Exception as e:
            logger.error(f"Click text error: {e}")
            return False
    
    # === SCROLLING ===
    
    async def scroll_like_human(self, direction: str = "down", amount: int = 300):
        """Scroll with human-like behavior"""
        scroll_amount = amount if direction == "down" else -amount
        
        # Scroll in small increments
        steps = random.randint(3, 7)
        per_step = scroll_amount // steps
        
        for _ in range(steps):
            await self.page.mouse.wheel(0, per_step + random.randint(-20, 20))
            await self._human_delay(50, 150)
        
        await self._human_delay(200, 500)
    
    async def scroll_to_element(self, selector: str):
        """Scroll element into view"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            await element.scroll_into_view_if_needed()
            await self._human_delay(300, 600)
        except Exception as e:
            logger.error(f"Scroll to element error: {e}")
    
    # === FORM HANDLING ===
    
    async def fill_form(self, fields: Dict[str, str]):
        """Fill multiple form fields"""
        for selector, value in fields.items():
            await self.type_like_human(selector, value)
            await self._human_delay(200, 400)
    
    async def select_option(self, selector: str, value: str):
        """Select dropdown option"""
        try:
            await self.page.select_option(selector, value)
            await self._human_delay(200, 400)
            return True
        except Exception as e:
            logger.error(f"Select error: {e}")
            return False
    
    async def check_checkbox(self, selector: str, check: bool = True):
        """Check or uncheck a checkbox"""
        try:
            is_checked = await self.page.is_checked(selector)
            if is_checked != check:
                await self.click_like_human(selector)
            return True
        except Exception as e:
            logger.error(f"Checkbox error: {e}")
            return False
    
    # === WAITING ===
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> Optional[ElementHandle]:
        """Wait for element to appear"""
        try:
            return await self.page.wait_for_selector(selector, timeout=timeout)
        except:
            return None
    
    async def wait_for_navigation(self, timeout: int = 30000):
        """Wait for navigation to complete"""
        try:
            await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except:
            pass
    
    async def wait_for_text(self, text: str, timeout: int = 30000) -> bool:
        """Wait for specific text to appear"""
        try:
            await self.page.wait_for_selector(f"text={text}", timeout=timeout)
            return True
        except:
            return False
    
    # === SCREENSHOTS ===
    
    async def screenshot(self, name: str = None) -> Path:
        """Take a screenshot"""
        screenshots_dir = DATA_DIR / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        filename = name or f"screenshot_{int(time.time())}"
        path = screenshots_dir / f"{filename}.png"
        
        await self.page.screenshot(path=str(path), full_page=True)
        logger.info(f"Screenshot saved: {path}")
        return path
    
    # === ELEMENT INFO ===
    
    async def get_element_text(self, selector: str) -> Optional[str]:
        """Get text content of element"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=5000)
            return await element.inner_text()
        except:
            return None
    
    async def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute of element"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=5000)
            return await element.get_attribute(attribute)
        except:
            return None
    
    async def get_all_links(self) -> List[Dict[str, str]]:
        """Get all links on page"""
        links = await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('a')).map(a => ({
                href: a.href,
                text: a.innerText.trim()
            }))
        """)
        return links
    
    async def get_all_inputs(self) -> List[Dict[str, str]]:
        """Get all input fields on page"""
        inputs = await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
                type: el.type || el.tagName.toLowerCase(),
                name: el.name,
                id: el.id,
                placeholder: el.placeholder
            }))
        """)
        return inputs
    
    # === NEW TAB ===
    
    async def new_tab(self, url: str = None) -> Page:
        """Open a new tab"""
        new_page = await self.context.new_page()
        if url:
            await new_page.goto(url)
        return new_page
    
    async def switch_to_tab(self, page: Page):
        """Switch to a specific tab"""
        self.page = page
        await page.bring_to_front()
    
    async def close_tab(self, page: Page = None):
        """Close a tab"""
        if page:
            await page.close()
        elif self.page:
            await self.page.close()
            pages = self.context.pages
            if pages:
                self.page = pages[-1]
    
    # === COOKIES & STORAGE ===
    
    async def get_cookies(self) -> List[Dict]:
        """Get all cookies"""
        return await self.context.cookies()
    
    async def set_cookies(self, cookies: List[Dict]):
        """Set cookies"""
        await self.context.add_cookies(cookies)
    
    async def clear_cookies(self):
        """Clear all cookies"""
        await self.context.clear_cookies()
    
    async def get_local_storage(self, key: str) -> Optional[str]:
        """Get localStorage item"""
        return await self.page.evaluate(f"localStorage.getItem('{key}')")
    
    async def set_local_storage(self, key: str, value: str):
        """Set localStorage item"""
        await self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")
    
    # === PRIVATE HELPERS ===
    
    async def _human_delay(self, min_ms: int, max_ms: int):
        """Add human-like random delay"""
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)


# Global browser instance
browser = BrowserController()
