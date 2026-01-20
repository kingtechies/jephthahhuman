"""
Jephthah Vision System
Screen capture and OCR for understanding what's on screen
"""

import asyncio
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import base64
from io import BytesIO

from PIL import Image
import pytesseract
from loguru import logger

from config.settings import DATA_DIR
from hands.browser import browser


class VisionSystem:
    """Visual understanding capabilities"""
    
    def __init__(self):
        self.screenshots_dir = DATA_DIR / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Vision system initialized")
    
    async def capture_screen(self, save_name: str = None) -> Image.Image:
        """Capture current browser screen"""
        path = await browser.screenshot(save_name)
        img = Image.open(path)
        logger.debug(f"Screen captured: {path}")
        return img
    
    async def read_screen_text(self) -> str:
        """Extract all text from current screen using OCR"""
        img = await self.capture_screen("ocr_temp")
        text = pytesseract.image_to_string(img)
        logger.debug(f"Extracted {len(text)} chars from screen")
        return text
    
    async def get_page_text(self) -> str:
        """Get text directly from DOM (faster than OCR)"""
        return await browser.get_page_text()
    
    async def find_text_on_screen(self, search_text: str) -> bool:
        """Check if specific text is visible on screen"""
        page_text = await self.get_page_text()
        found = search_text.lower() in page_text.lower()
        logger.debug(f"Text '{search_text}' found: {found}")
        return found
    
    async def find_button(self, button_text: str) -> Optional[str]:
        """Find a button by its text and return selector"""
        selectors = [
            f"button:has-text('{button_text}')",
            f"input[type='button'][value*='{button_text}']",
            f"input[type='submit'][value*='{button_text}']",
            f"a:has-text('{button_text}')",
            f"[role='button']:has-text('{button_text}')",
        ]
        
        for selector in selectors:
            element = await browser.wait_for_selector(selector, timeout=2000)
            if element:
                logger.debug(f"Found button: {selector}")
                return selector
        
        return None
    
    async def find_input_field(self, label_text: str = None, field_type: str = None, 
                              placeholder: str = None) -> Optional[str]:
        """Find an input field by label, type, or placeholder"""
        inputs = await browser.get_all_inputs()
        
        for inp in inputs:
            if placeholder and placeholder.lower() in (inp.get('placeholder', '') or '').lower():
                if inp.get('id'):
                    return f"#{inp['id']}"
                elif inp.get('name'):
                    return f"[name='{inp['name']}']"
            
            if field_type and inp.get('type') == field_type:
                if inp.get('id'):
                    return f"#{inp['id']}"
                elif inp.get('name'):
                    return f"[name='{inp['name']}']"
        
        # Try to find by label
        if label_text:
            label_selector = f"label:has-text('{label_text}')"
            try:
                label = await browser.page.wait_for_selector(label_selector, timeout=2000)
                if label:
                    for_attr = await label.get_attribute('for')
                    if for_attr:
                        return f"#{for_attr}"
            except:
                pass
        
        return None
    
    async def find_link(self, link_text: str) -> Optional[str]:
        """Find a link by its text"""
        links = await browser.get_all_links()
        
        for link in links:
            if link_text.lower() in link.get('text', '').lower():
                return link.get('href')
        
        return None
    
    async def get_form_fields(self) -> List[Dict]:
        """Get all form fields on current page"""
        return await browser.get_all_inputs()
    
    async def detect_captcha(self) -> bool:
        """Detect if CAPTCHA is present on page"""
        captcha_indicators = [
            "captcha",
            "recaptcha",
            "hcaptcha", 
            "challenge",
            "verify you're human",
            "i'm not a robot",
            "security check",
        ]
        
        page_text = await self.get_page_text()
        page_text_lower = page_text.lower()
        
        for indicator in captcha_indicators:
            if indicator in page_text_lower:
                logger.warning("CAPTCHA detected!")
                return True
        
        # Check for reCAPTCHA iframe
        try:
            recaptcha = await browser.wait_for_selector(
                "iframe[src*='recaptcha'], iframe[src*='hcaptcha']",
                timeout=1000
            )
            if recaptcha:
                logger.warning("CAPTCHA iframe detected!")
                return True
        except:
            pass
        
        return False
    
    async def detect_error(self) -> Optional[str]:
        """Detect error messages on page"""
        error_selectors = [
            ".error",
            ".alert-danger",
            ".alert-error",
            "[role='alert']",
            ".error-message",
            ".form-error",
        ]
        
        for selector in error_selectors:
            try:
                element = await browser.wait_for_selector(selector, timeout=1000)
                if element:
                    text = await element.inner_text()
                    if text.strip():
                        logger.warning(f"Error detected: {text[:100]}")
                        return text.strip()
            except:
                continue
        
        return None
    
    async def detect_success(self) -> Optional[str]:
        """Detect success messages on page"""
        success_selectors = [
            ".success",
            ".alert-success",
            ".success-message",
            "[role='status']",
        ]
        
        success_keywords = [
            "success",
            "thank you",
            "completed",
            "confirmed",
            "submitted",
            "created",
            "registered",
        ]
        
        for selector in success_selectors:
            try:
                element = await browser.wait_for_selector(selector, timeout=1000)
                if element:
                    text = await element.inner_text()
                    if text.strip():
                        logger.info(f"Success detected: {text[:100]}")
                        return text.strip()
            except:
                continue
        
        # Check page text for success keywords
        page_text = await self.get_page_text()
        for keyword in success_keywords:
            if keyword.lower() in page_text.lower():
                return keyword
        
        return None
    
    async def is_logged_in(self, indicators: List[str] = None) -> bool:
        """Check if currently logged in"""
        default_indicators = [
            "log out",
            "logout", 
            "sign out",
            "signout",
            "my account",
            "profile",
            "dashboard",
        ]
        
        indicators = indicators or default_indicators
        page_text = await self.get_page_text()
        page_text_lower = page_text.lower()
        
        for indicator in indicators:
            if indicator.lower() in page_text_lower:
                return True
        
        return False
    
    async def get_page_structure(self) -> Dict:
        """Get high-level structure of current page"""
        return {
            "url": await browser.get_current_url(),
            "title": await browser.get_page_title(),
            "has_captcha": await self.detect_captcha(),
            "is_logged_in": await self.is_logged_in(),
            "error": await self.detect_error(),
            "success": await self.detect_success(),
            "forms": await self.get_form_fields(),
            "links_count": len(await browser.get_all_links()),
        }


# Global vision instance  
vision = VisionSystem()
