"""
Jephthah Account Registrar
Register accounts like a REAL HUMAN - no APIs
"""

import asyncio
import random
import string
from datetime import datetime
from typing import Dict, Optional

from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.vision import vision
from eyes.perception import perception
from brain.memory import memory
from brain.autonomous import brain


class AccountRegistrar:
    """Register accounts on any platform like a human"""
    
    def __init__(self):
        self.email = config.identity.email
        self.registered_accounts: Dict[str, Dict] = {}
        
    def generate_password(self, length: int = 16) -> str:
        """Generate a secure password"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(random.choice(chars) for _ in range(length))
        return password
    
    def generate_username(self, base: str = "jephthah") -> str:
        """Generate a unique username"""
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{base}{suffix}"
    
    async def register(self, platform: str, url: str) -> Dict:
        """Register on any platform - fully automated"""
        logger.info(f"Starting registration on {platform}")
        
        result = {
            "platform": platform,
            "status": "pending",
            "username": None,
            "password": None,
            "email": self.email
        }
        
        try:
            # Navigate to registration page
            await browser.goto(url)
            await asyncio.sleep(2)
            
            # Read the page
            understanding = await perception.read_and_understand()
            
            # Decide what to do
            decision = brain.think(f"Registration page for {platform}")
            logger.info(f"Brain decided: {decision}")
            
            # Generate credentials
            username = self.generate_username()
            password = self.generate_password()
            
            # Find and fill form fields
            await self._fill_registration_form(username, password)
            
            # Wait a bit (human-like)
            await asyncio.sleep(random.uniform(1, 3))
            
            # Submit
            await self._submit_form()
            
            # Wait for response
            await asyncio.sleep(3)
            
            # Check for OTP/verification
            page_text = await browser.get_page_text()
            if "verification" in page_text.lower() or "otp" in page_text.lower() or "code" in page_text.lower():
                otp = await self._handle_verification()
                if otp:
                    logger.info(f"Verification completed with OTP: {otp}")
            
            # Check for success
            if await vision.detect_success() or await vision.is_logged_in():
                result["status"] = "success"
                result["username"] = username
                result["password"] = password
                
                # Store in memory
                self._store_account(platform, result)
                
                logger.info(f"✅ Registered on {platform}: {username}")
            else:
                # Check for error
                error = await vision.detect_error()
                if error:
                    result["status"] = "failed"
                    result["error"] = error
                    logger.warning(f"Registration failed: {error}")
                else:
                    result["status"] = "unknown"
            
            return result
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            result["status"] = "error"
            result["error"] = str(e)
            return result
    
    async def _fill_registration_form(self, username: str, password: str):
        """Fill registration form fields"""
        
        # Common field patterns
        field_patterns = {
            "email": ["email", "mail", "e-mail"],
            "username": ["username", "user", "name", "handle"],
            "password": ["password", "pass", "pwd"],
            "confirm_password": ["confirm", "repeat", "verify"],
            "name": ["full name", "name", "displayname"],
            "first_name": ["first", "firstname", "fname"],
            "last_name": ["last", "lastname", "lname"],
        }
        
        # Try to fill each field type
        for field_type, patterns in field_patterns.items():
            for pattern in patterns:
                try:
                    if field_type == "email":
                        success = await perception.find_and_type(pattern, self.email)
                    elif field_type == "username":
                        success = await perception.find_and_type(pattern, username)
                    elif field_type in ["password", "confirm_password"]:
                        success = await perception.find_and_type(pattern, password)
                    elif field_type == "name":
                        success = await perception.find_and_type(pattern, "Jephthah Ameh")
                    elif field_type == "first_name":
                        success = await perception.find_and_type(pattern, "Jephthah")
                    elif field_type == "last_name":
                        success = await perception.find_and_type(pattern, "Ameh")
                    
                    if success:
                        logger.debug(f"Filled {field_type}")
                        break
                except:
                    continue
        
        # Check for checkboxes (terms, age verification)
        try:
            checkboxes = await browser.page.query_selector_all('input[type="checkbox"]')
            for cb in checkboxes[:3]:  # First 3 checkboxes
                await cb.check()
        except:
            pass
    
    async def _submit_form(self):
        """Submit the registration form"""
        submit_texts = [
            "Sign up", "Register", "Create account", "Submit",
            "Get started", "Join", "Continue", "Next"
        ]
        
        for text in submit_texts:
            try:
                clicked = await perception.find_and_click(text)
                if clicked:
                    logger.info(f"Clicked submit: {text}")
                    return True
            except:
                continue
        
        # Try submit button directly
        try:
            await browser.click_like_human('button[type="submit"]')
            return True
        except:
            pass
        
        return False
    
    async def _handle_verification(self) -> Optional[str]:
        """Handle email/OTP verification"""
        logger.info("Handling verification...")
        
        # Wait for OTP (check email page or current page)
        otp = await perception.wait_for_otp(timeout=60)
        
        if otp:
            # Find OTP input and enter it
            otp_fields = ["code", "otp", "verification", "pin", "token"]
            for field in otp_fields:
                try:
                    success = await perception.find_and_type(field, otp)
                    if success:
                        await asyncio.sleep(1)
                        await self._submit_form()
                        return otp
                except:
                    continue
        
        return None
    
    def _store_account(self, platform: str, account: Dict):
        """Store account credentials"""
        self.registered_accounts[platform] = account
        
        # Store in memory
        memory.register_account(
            platform=platform,
            username=account["username"],
            email=account["email"],
            password_key=f"{platform.upper()}_PASSWORD"
        )
        
        # Save password to jeph.env
        config.save_credential(f"{platform.upper()}_USERNAME", account["username"])
        config.save_credential(f"{platform.upper()}_PASSWORD", account["password"])
        
        logger.info(f"Credentials stored for {platform}")
    
    async def register_twitter(self) -> Dict:
        """Register on Twitter/X"""
        return await self.register("twitter", "https://x.com/i/flow/signup")
    
    async def register_linkedin(self) -> Dict:
        """Register on LinkedIn"""
        return await self.register("linkedin", "https://www.linkedin.com/signup")
    
    async def register_medium(self) -> Dict:
        """Register on Medium"""
        return await self.register("medium", "https://medium.com/m/signin")
    
    async def register_upwork(self) -> Dict:
        """Register on Upwork"""
        return await self.register("upwork", "https://www.upwork.com/nx/signup/")
    
    async def register_github(self) -> Dict:
        """Register on GitHub"""
        return await self.register("github", "https://github.com/signup")


# Global registrar instance
registrar = AccountRegistrar()
