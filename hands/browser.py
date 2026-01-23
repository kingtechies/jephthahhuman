"""
Jephthah Browser Controller
Human-like browser automation with Playwright - Enhanced with retry logic and error handling
"""

import asyncio
import random
import time
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
from functools import wraps

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle, TimeoutError as PlaywrightTimeout
from loguru import logger

from config.settings import config, DATA_DIR


def retry_async(max_retries: int = 3, base_delay: float = 1.0, exceptions=(Exception,)):
    """Decorator for async retry with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
            raise last_exception
        return wrapper
    return decorator


class BrowserController:
    """Human-like browser automation with retry logic and error recovery"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.user_data_dir = DATA_DIR / "browser_profile"
        self._is_initialized = False
        self._error_screenshots_dir = DATA_DIR / "error_screenshots"
        self._last_successful_url = None
        
    async def initialize(self, headless: bool = False):
        """Initialize the browser with retry - HEADFUL by default for real interactions"""
        if self._is_initialized:
            return
        
        self._error_screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(3):
            try:
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
                        '--ignore-certificate-errors',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                    ]
                )
                
                self.context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    locale='en-GB',
                    timezone_id='Europe/London',
                    permissions=['geolocation'],
                    geolocation={'latitude': 51.5074, 'longitude': -0.1278},
                    extra_http_headers={
                        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
                logger.info("🌐 Browser initialized successfully")
                return
                
            except Exception as e:
                logger.error(f"Browser init failed (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(f"Failed to initialize browser after 3 attempts: {e}")
    
    async def close(self):
        """Close the browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self._is_initialized = False
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def _ensure_initialized(self):
        """Ensure browser is initialized"""
        if not self._is_initialized:
            await self.initialize(headless=True)
    
    async def _recover_page(self):
        """Attempt to recover from page crash"""
        try:
            if self.context:
                pages = self.context.pages
                if pages:
                    self.page = pages[-1]
                    return True
                else:
                    self.page = await self.context.new_page()
                    return True
        except Exception as e:
            logger.error(f"Page recovery failed: {e}")
            return False
    
    async def _screenshot_on_error(self, error_name: str):
        """Take screenshot when error occurs for debugging"""
        try:
            timestamp = int(time.time())
            path = self._error_screenshots_dir / f"error_{error_name}_{timestamp}.png"
            await self.page.screenshot(path=str(path), full_page=True)
            logger.info(f"📸 Error screenshot saved: {path}")
            return path
        except:
            return None
    
    # === NAVIGATION ===
    
    @retry_async(max_retries=3, base_delay=2.0)
    async def goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000) -> bool:
        """Navigate to a URL with retry logic"""
        await self._ensure_initialized()
        
        try:
            await self._human_delay(500, 1500)
            response = await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            await self._human_delay(1000, 2000)
            
            self._last_successful_url = url
            logger.info(f"🔗 Navigated to: {url}")
            return response.ok if response else False
            
        except PlaywrightTimeout as e:
            logger.warning(f"Navigation timeout for {url}: {e}")
            await self._screenshot_on_error("timeout")
            raise
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            await self._screenshot_on_error("navigation")
            raise
    
    async def goto_safe(self, url: str, timeout: int = 30000) -> bool:
        """Navigate with fallback (doesn't raise on failure)"""
        try:
            return await self.goto(url, timeout=timeout)
        except Exception as e:
            logger.error(f"Safe navigation failed: {e}")
            return False
    
    async def get_current_url(self) -> str:
        """Get current page URL"""
        await self._ensure_initialized()
        return self.page.url
    
    async def get_page_title(self) -> str:
        """Get current page title"""
        await self._ensure_initialized()
        return await self.page.title()
    
    async def get_page_content(self) -> str:
        """Get page HTML content"""
        await self._ensure_initialized()
        return await self.page.content()
    
    async def get_page_text(self) -> str:
        """Get all visible text on page"""
        await self._ensure_initialized()
        try:
            return await self.page.inner_text('body')
        except:
            return ""
    
    # === HUMAN-LIKE TYPING ===
    
    @retry_async(max_retries=2, base_delay=1.0)
    async def type_like_human(self, selector: str, text: str, clear_first: bool = True) -> bool:
        """Type text with human-like delays and retry"""
        await self._ensure_initialized()
        
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
            
            logger.debug(f"⌨️ Typed into {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Type error: {e}")
            raise
    
    # === CLICKING ===
    
    @retry_async(max_retries=2, base_delay=1.0)
    async def click_like_human(self, selector: str) -> bool:
        """Click with human-like behavior and retry"""
        await self._ensure_initialized()
        
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
            logger.debug(f"🖱️ Clicked: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Click error: {e}")
            raise
    
    async def click_text(self, text: str) -> bool:
        """Click element containing specific text"""
        await self._ensure_initialized()
        
        try:
            await self.page.click(f"text={text}", timeout=5000)
            await self._human_delay(200, 500)
            return True
        except Exception as e:
            logger.debug(f"Click text error: {e}")
            return False
    
    async def click_text_safe(self, text: str) -> bool:
        """Click text element, return False instead of raising"""
        try:
            return await self.click_text(text)
        except:
            return False
    
    # === SCROLLING ===
    
    async def scroll_like_human(self, direction: str = "down", amount: int = 300):
        """Scroll with human-like behavior"""
        await self._ensure_initialized()
        
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
        await self._ensure_initialized()
        
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            await element.scroll_into_view_if_needed()
            await self._human_delay(300, 600)
        except Exception as e:
            logger.debug(f"Scroll to element error: {e}")
    
    # === FORM HANDLING ===
    
    async def fill_form(self, fields: Dict[str, str]):
        """Fill multiple form fields"""
        for selector, value in fields.items():
            try:
                await self.type_like_human(selector, value)
            except:
                pass
            await self._human_delay(200, 400)
    
    async def select_option(self, selector: str, value: str) -> bool:
        """Select dropdown option"""
        await self._ensure_initialized()
        
        try:
            await self.page.select_option(selector, value)
            await self._human_delay(200, 400)
            return True
        except Exception as e:
            logger.error(f"Select error: {e}")
            return False
    
    async def check_checkbox(self, selector: str, check: bool = True) -> bool:
        """Check or uncheck a checkbox"""
        await self._ensure_initialized()
        
        try:
            is_checked = await self.page.is_checked(selector)
            if is_checked != check:
                await self.click_like_human(selector)
            return True
        except Exception as e:
            logger.debug(f"Checkbox error: {e}")
            return False
    
    # === WAITING ===
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> Optional[ElementHandle]:
        """Wait for element to appear"""
        await self._ensure_initialized()
        
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
        await self._ensure_initialized()
        
        try:
            await self.page.wait_for_selector(f"text={text}", timeout=timeout)
            return True
        except:
            return False
    
    # === SCREENSHOTS ===
    
    async def screenshot(self, name: str = None) -> Path:
        """Take a screenshot"""
        await self._ensure_initialized()
        
        screenshots_dir = DATA_DIR / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        filename = name or f"screenshot_{int(time.time())}"
        path = screenshots_dir / f"{filename}.png"
        
        await self.page.screenshot(path=str(path), full_page=True)
        logger.info(f"📸 Screenshot saved: {path}")
        return path
    
    # === ELEMENT INFO ===
    
    async def get_element_text(self, selector: str) -> Optional[str]:
        """Get text content of element"""
        await self._ensure_initialized()
        
        try:
            element = await self.page.wait_for_selector(selector, timeout=5000)
            return await element.inner_text()
        except:
            return None
    
    async def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute of element"""
        await self._ensure_initialized()
        
        try:
            element = await self.page.wait_for_selector(selector, timeout=5000)
            return await element.get_attribute(attribute)
        except:
            return None
    
    async def get_all_links(self) -> List[Dict[str, str]]:
        """Get all links on page"""
        await self._ensure_initialized()
        
        try:
            links = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('a')).map(a => ({
                    href: a.href,
                    text: a.innerText.trim()
                }))
            """)
            return links
        except:
            return []
    
    async def get_all_inputs(self) -> List[Dict[str, str]]:
        """Get all input fields on page"""
        await self._ensure_initialized()
        
        try:
            inputs = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
                    type: el.type || el.tagName.toLowerCase(),
                    name: el.name,
                    id: el.id,
                    placeholder: el.placeholder
                }))
            """)
            return inputs
        except:
            return []
    
    # === NEW TAB ===
    
    async def new_tab(self, url: str = None) -> Page:
        """Open a new tab"""
        await self._ensure_initialized()
        
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
        await self._ensure_initialized()
        return await self.context.cookies()
    
    async def set_cookies(self, cookies: List[Dict]):
        """Set cookies"""
        await self._ensure_initialized()
        await self.context.add_cookies(cookies)
    
    async def clear_cookies(self):
        """Clear all cookies"""
        await self._ensure_initialized()
        await self.context.clear_cookies()
    
    async def get_local_storage(self, key: str) -> Optional[str]:
        """Get localStorage item"""
        await self._ensure_initialized()
        return await self.page.evaluate(f"localStorage.getItem('{key}')")
    
    async def set_local_storage(self, key: str, value: str):
        """Set localStorage item"""
        await self._ensure_initialized()
        await self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")
    
    # === PRIVATE HELPERS ===
    
    async def _human_delay(self, min_ms: int, max_ms: int):
        """Add human-like random delay"""
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)


# Global browser instance
browser = BrowserController()
