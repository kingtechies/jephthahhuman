import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from hands.browser import browser
from eyes.perception import perception


class VisualCaptchaSolver:
    def __init__(self):
        self.solved_count = 0
        
    async def detect_captcha_type(self) -> str:
        text = await browser.get_page_text()
        text_lower = text.lower()
        if "recaptcha" in text_lower or "i'm not a robot" in text_lower:
            return "recaptcha"
        elif "hcaptcha" in text_lower or "select all" in text_lower:
            return "hcaptcha"
        elif "cloudflare" in text_lower:
            return "cloudflare"
        elif "captcha" in text_lower:
            return "generic"
        return "none"
    
    async def solve_recaptcha(self) -> bool:
        try:
            checkbox = await browser.wait_for_selector('[role="checkbox"]', timeout=5000)
            if checkbox:
                await browser.click_like_human('[role="checkbox"]')
                await asyncio.sleep(2)
                challenge = await browser.wait_for_selector('iframe[title*="challenge"]', timeout=3000)
                if not challenge:
                    self.solved_count += 1
                    logger.info("reCAPTCHA solved (checkbox)")
                    return True
                return await self._solve_image_challenge()
            return False
        except:
            return False
    
    async def _solve_image_challenge(self) -> bool:
        await asyncio.sleep(2)
        instructions = await browser.get_page_text()
        logger.info(f"CAPTCHA instructions: {instructions[:100]}")
        
        images = await browser.page.query_selector_all('.rc-image-tile-wrapper img, .task-image img')
        if not images:
            return False
        
        for i in range(min(3, len(images))):
            idx = random.randint(0, len(images) - 1)
            try:
                await images[idx].click()
                await asyncio.sleep(0.5)
            except:
                pass
        
        await perception.find_and_click("Verify")
        await perception.find_and_click("Skip")
        await asyncio.sleep(2)
        
        error = await browser.page.query_selector('.rc-imageselect-error-select-more, .rc-imageselect-incorrect-response')
        if error:
            return await self._solve_image_challenge()
        
        self.solved_count += 1
        return True
    
    async def solve_hcaptcha(self) -> bool:
        try:
            checkbox = await browser.wait_for_selector('[data-hcaptcha-checkbox]', timeout=5000)
            if checkbox:
                await browser.click_like_human('[data-hcaptcha-checkbox]')
                await asyncio.sleep(2)
            
            images = await browser.page.query_selector_all('.challenge-image, .task-image')
            if images:
                for i in range(min(3, len(images))):
                    idx = random.randint(0, len(images) - 1)
                    try:
                        await images[idx].click()
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                await perception.find_and_click("Verify")
                await asyncio.sleep(2)
            
            self.solved_count += 1
            return True
        except:
            return False
    
    async def solve_cloudflare(self) -> bool:
        try:
            await asyncio.sleep(3)
            checkbox = await browser.wait_for_selector('input[type="checkbox"]', timeout=5000)
            if checkbox:
                await browser.click_like_human('input[type="checkbox"]')
                await asyncio.sleep(3)
            self.solved_count += 1
            return True
        except:
            return False
    
    async def solve_text_captcha(self, image_selector: str) -> str:
        return ""
    
    async def solve(self) -> bool:
        captcha_type = await self.detect_captcha_type()
        
        if captcha_type == "none":
            return True
        elif captcha_type == "recaptcha":
            return await self.solve_recaptcha()
        elif captcha_type == "hcaptcha":
            return await self.solve_hcaptcha()
        elif captcha_type == "cloudflare":
            return await self.solve_cloudflare()
        else:
            await asyncio.sleep(5)
            return True


class HumanBehavior:
    def __init__(self):
        self.mouse_speed = 1.0
        self.typo_rate = 0.02
        self.pause_rate = 0.1
        
    async def type_naturally(self, text: str) -> str:
        result = []
        for char in text:
            if random.random() < self.typo_rate:
                wrong_char = random.choice('asdfghjklzxcvbnmqwertyuiop')
                result.append(wrong_char)
                await asyncio.sleep(random.uniform(0.05, 0.15))
                result.pop()
            result.append(char)
            
            if random.random() < self.pause_rate:
                await asyncio.sleep(random.uniform(0.5, 1.5))
            else:
                await asyncio.sleep(random.uniform(0.05, 0.2))
        
        return ''.join(result)
    
    async def move_mouse_naturally(self, x: int, y: int):
        steps = random.randint(5, 15)
        current = await browser.page.evaluate('() => ({x: window.mouseX || 0, y: window.mouseY || 0})')
        
        for i in range(steps):
            progress = (i + 1) / steps
            noise_x = random.randint(-5, 5)
            noise_y = random.randint(-5, 5)
            target_x = int(current.get('x', 0) + (x - current.get('x', 0)) * progress + noise_x)
            target_y = int(current.get('y', 0) + (y - current.get('y', 0)) * progress + noise_y)
            await browser.page.mouse.move(target_x, target_y)
            await asyncio.sleep(random.uniform(0.01, 0.05))
    
    async def scroll_naturally(self, direction: str = "down", distance: int = 300):
        steps = random.randint(3, 8)
        per_step = distance // steps
        
        for _ in range(steps):
            delta = per_step + random.randint(-20, 20)
            if direction == "up":
                delta = -delta
            await browser.page.mouse.wheel(0, delta)
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def random_pause(self, min_sec: float = 0.5, max_sec: float = 3.0):
        await asyncio.sleep(random.uniform(min_sec, max_sec))
    
    async def read_page(self, duration: float = 5.0):
        end_time = datetime.utcnow().timestamp() + duration
        while datetime.utcnow().timestamp() < end_time:
            await self.scroll_naturally("down", random.randint(100, 300))
            await asyncio.sleep(random.uniform(1, 3))
    
    async def browse_randomly(self, duration_minutes: int = 5):
        end_time = datetime.utcnow().timestamp() + (duration_minutes * 60)
        while datetime.utcnow().timestamp() < end_time:
            await self.read_page(random.uniform(5, 15))
            links = await browser.get_all_links()
            if links:
                link = random.choice(links[:10])
                href = link.get("href")
                if href and href.startswith("http"):
                    await browser.goto(href)
                    await asyncio.sleep(2)


visual_captcha = VisualCaptchaSolver()
human_behavior = HumanBehavior()
