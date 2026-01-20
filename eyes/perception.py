"""
Jephthah Real-Time Perception
See, understand, and react in real time - like a human
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import re

from loguru import logger

from hands.browser import browser
from eyes.vision import vision
from brain.memory import memory, MemoryType


class RealTimePerception:
    """Real-time visual understanding - THE EYES THAT NEVER SLEEP"""
    
    def __init__(self):
        self.is_watching = False
        self.current_context: Dict = {}
        self.detected_elements: List[Dict] = []
        self.callbacks: Dict[str, Callable] = {}
        
        # Pattern recognition
        self.otp_pattern = re.compile(r'\b(\d{4,8})\b')
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        self.url_pattern = re.compile(r'https?://[\w\.-]+[\w/\-_.~:?#\[\]@!$&\'()*+,;=%]*')
        self.money_pattern = re.compile(r'\$[\d,]+\.?\d*')
        
        logger.info("Real-time perception initialized")
    
    async def start_watching(self):
        """Start real-time perception loop"""
        self.is_watching = True
        logger.info("👁️ EYES ACTIVE - Watching in real-time")
        
        while self.is_watching:
            await self._perceive()
            await asyncio.sleep(0.5)  # 500ms refresh rate
    
    async def stop_watching(self):
        """Stop watching"""
        self.is_watching = False
    
    async def _perceive(self):
        """Take a snapshot of current state"""
        try:
            self.current_context = {
                "timestamp": datetime.utcnow().isoformat(),
                "url": await browser.get_current_url(),
                "title": await browser.get_page_title(),
                "page_text": await browser.get_page_text(),
            }
            
            # Detect important elements
            await self._detect_elements()
            
            # Trigger callbacks for detected patterns
            await self._process_detections()
            
        except Exception as e:
            logger.debug(f"Perception cycle error: {e}")
    
    async def _detect_elements(self):
        """Detect important elements on page"""
        self.detected_elements = []
        text = self.current_context.get("page_text", "")
        
        # Detect OTP codes
        otps = self.otp_pattern.findall(text)
        for otp in otps:
            if len(otp) >= 4 and len(otp) <= 8:
                self.detected_elements.append({
                    "type": "otp",
                    "value": otp,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Detect money amounts
        amounts = self.money_pattern.findall(text)
        for amount in amounts:
            self.detected_elements.append({
                "type": "money",
                "value": amount
            })
        
        # Detect forms
        forms = await browser.get_all_inputs()
        if forms:
            self.detected_elements.append({
                "type": "form",
                "fields": forms[:10]  # First 10 fields
            })
        
        # Detect buttons
        buttons = await self._find_buttons()
        for btn in buttons:
            self.detected_elements.append({
                "type": "button",
                "text": btn
            })
    
    async def _find_buttons(self) -> List[str]:
        """Find all clickable buttons"""
        try:
            buttons = await browser.page.evaluate("""
                () => Array.from(document.querySelectorAll('button, input[type="submit"], a.btn, [role="button"]'))
                    .map(el => el.innerText || el.value || el.getAttribute('aria-label'))
                    .filter(text => text && text.trim().length > 0)
                    .slice(0, 20)
            """)
            return buttons
        except:
            return []
    
    async def _process_detections(self):
        """Process detected elements and trigger callbacks"""
        for element in self.detected_elements:
            callback = self.callbacks.get(element["type"])
            if callback:
                await callback(element)
    
    def on_detect(self, element_type: str, callback: Callable):
        """Register callback for detection type"""
        self.callbacks[element_type] = callback
    
    async def wait_for_otp(self, timeout: int = 120) -> Optional[str]:
        """Wait for OTP to appear on screen"""
        logger.info(f"Waiting for OTP (timeout: {timeout}s)")
        
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).seconds < timeout:
            text = await browser.get_page_text()
            otps = self.otp_pattern.findall(text)
            
            # Filter to likely OTPs (4-8 digits)
            for otp in otps:
                if len(otp) >= 4 and len(otp) <= 8:
                    logger.info(f"OTP detected: {otp}")
                    return otp
            
            await asyncio.sleep(1)
        
        logger.warning("OTP timeout")
        return None
    
    async def read_and_understand(self, selector: str = "body") -> Dict:
        """Read and understand content on page"""
        try:
            text = await browser.get_element_text(selector) or await browser.get_page_text()
            
            understanding = {
                "raw_text": text[:5000],
                "word_count": len(text.split()),
                "has_form": bool(await browser.get_all_inputs()),
                "has_error": await vision.detect_error(),
                "has_success": await vision.detect_success(),
                "detected_otps": self.otp_pattern.findall(text),
                "detected_emails": self.email_pattern.findall(text),
                "detected_urls": self.url_pattern.findall(text)[:5],
                "detected_amounts": self.money_pattern.findall(text),
            }
            
            return understanding
            
        except Exception as e:
            logger.error(f"Read error: {e}")
            return {}
    
    async def what_do_i_see(self) -> str:
        """Describe what's currently visible - human-like awareness"""
        ctx = self.current_context
        
        description = f"""
CURRENT VIEW:
- URL: {ctx.get('url', 'unknown')}
- Page: {ctx.get('title', 'unknown')}
- Text preview: {ctx.get('page_text', '')[:200]}...

DETECTED:
"""
        for elem in self.detected_elements[:10]:
            description += f"- {elem['type']}: {elem.get('value', elem.get('text', 'N/A'))}\n"
        
        return description
    
    async def find_and_click(self, target: str) -> bool:
        """Find something by description and click it"""
        # Try different selectors
        selectors = [
            f"text={target}",
            f'button:has-text("{target}")',
            f'a:has-text("{target}")',
            f'[aria-label*="{target}"]',
            f'input[value*="{target}"]',
        ]
        
        for selector in selectors:
            try:
                element = await browser.wait_for_selector(selector, timeout=2000)
                if element:
                    await browser.click_like_human(selector)
                    logger.info(f"Clicked: {target}")
                    return True
            except:
                continue
        
        logger.warning(f"Could not find: {target}")
        return False
    
    async def find_and_type(self, field_hint: str, text: str) -> bool:
        """Find an input by hint and type into it"""
        selectors = [
            f'input[placeholder*="{field_hint}" i]',
            f'input[name*="{field_hint}" i]',
            f'input[id*="{field_hint}" i]',
            f'textarea[placeholder*="{field_hint}" i]',
        ]
        
        for selector in selectors:
            try:
                element = await browser.wait_for_selector(selector, timeout=2000)
                if element:
                    await browser.type_like_human(selector, text)
                    logger.info(f"Typed into: {field_hint}")
                    return True
            except:
                continue
        
        logger.warning(f"Could not find field: {field_hint}")
        return False


# Global perception instance
perception = RealTimePerception()
