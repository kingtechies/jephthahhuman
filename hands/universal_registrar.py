import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.perception import perception
from hands.human import visual_captcha, human_behavior


class UniversalRegistrar:
    def __init__(self):
        self.email = config.identity.email
        self.name = "Jephthah Ameh"
        self.registered = {}
        
    async def register_anywhere(self, url: str, platform_name: str = "") -> Dict:
        result = {"platform": platform_name or url, "status": "pending"}
        
        try:
            await browser.goto(url)
            await asyncio.sleep(2)
            
            if await visual_captcha.detect_captcha_type() != "none":
                await visual_captcha.solve()
            
            await self._fill_signup_form()
            await self._submit_form()
            await asyncio.sleep(3)
            
            if await visual_captcha.detect_captcha_type() != "none":
                await visual_captcha.solve()
            
            from voice.otp_handler import otp_handler
            page_text = await browser.get_page_text()
            if any(w in page_text.lower() for w in ["verify", "otp", "code", "confirmation"]):
                otp = await otp_handler.wait_for_otp_email(timeout=120)
                if otp:
                    await perception.find_and_type("code", otp)
                    await perception.find_and_type("otp", otp)
                    await perception.find_and_type("verification", otp)
                    await self._submit_form()
            
            page_text = await browser.get_page_text()
            if any(w in page_text.lower() for w in ["welcome", "success", "dashboard", "profile", "home"]):
                result["status"] = "success"
                result["username"] = self._extract_username(page_text)
                self.registered[platform_name] = result
                self._save_credentials(platform_name)
                logger.info(f"Registered on {platform_name}")
            else:
                result["status"] = "uncertain"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result
    
    async def _fill_signup_form(self):
        username = f"jephthah{random.randint(100, 9999)}"
        password = self._generate_password()
        
        fields = [
            ("email", self.email),
            ("e-mail", self.email),
            ("mail", self.email),
            ("username", username),
            ("user", username),
            ("name", self.name),
            ("fullname", self.name),
            ("full name", self.name),
            ("first", "Jephthah"),
            ("last", "Ameh"),
            ("password", password),
            ("pass", password),
            ("confirm", password),
            ("repeat", password),
        ]
        
        for hint, value in fields:
            await perception.find_and_type(hint, value)
        
        checkboxes = await browser.page.query_selector_all('input[type="checkbox"]')
        for cb in checkboxes:
            try:
                await cb.check()
            except:
                pass
        
        config.save_credential(f"LAST_PASSWORD", password)
        config.save_credential(f"LAST_USERNAME", username)
    
    async def _submit_form(self):
        buttons = ["Sign up", "Register", "Create", "Submit", "Join", "Get started", "Continue", "Next"]
        for btn in buttons:
            clicked = await perception.find_and_click(btn)
            if clicked:
                await asyncio.sleep(2)
                return
        try:
            await browser.click_like_human('button[type="submit"]')
        except:
            pass
    
    def _generate_password(self) -> str:
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
        return "Jeph" + ''.join(random.choices(chars, k=12))
    
    def _extract_username(self, text: str) -> str:
        return ""
    
    def _save_credentials(self, platform: str):
        pass
    
    async def register_ai_platform(self, platform: str) -> Dict:
        platforms = {
            "chatgpt": "https://chat.openai.com/auth/login",
            "claude": "https://claude.ai/login",
            "gemini": "https://gemini.google.com",
            "perplexity": "https://www.perplexity.ai/signup",
            "copilot": "https://copilot.microsoft.com",
            "poe": "https://poe.com/login",
            "you": "https://you.com",
            "phind": "https://www.phind.com",
        }
        url = platforms.get(platform)
        if url:
            return await self.register_anywhere(url, platform)
        return {"status": "unknown_platform"}
    
    async def register_all_social(self) -> List[Dict]:
        platforms = {
            "twitter": "https://twitter.com/i/flow/signup",
            "linkedin": "https://www.linkedin.com/signup",
            "facebook": "https://www.facebook.com/r.php",
            "instagram": "https://www.instagram.com/accounts/emailsignup/",
            "tiktok": "https://www.tiktok.com/signup",
            "medium": "https://medium.com/m/signin",
            "reddit": "https://www.reddit.com/register/",
            "pinterest": "https://www.pinterest.com/",
            "youtube": "https://accounts.google.com/signup",
        }
        results = []
        for name, url in platforms.items():
            result = await self.register_anywhere(url, name)
            results.append(result)
            await asyncio.sleep(60)
        return results
    
    async def register_all_freelance(self) -> List[Dict]:
        platforms = {
            "upwork": "https://www.upwork.com/nx/signup/",
            "fiverr": "https://www.fiverr.com/join",
            "freelancer": "https://www.freelancer.com/signup",
            "toptal": "https://www.toptal.com/talent/apply",
            "guru": "https://www.guru.com/pro/join.aspx",
            "peopleperhour": "https://www.peopleperhour.com/site/register",
        }
        results = []
        for name, url in platforms.items():
            result = await self.register_anywhere(url, name)
            results.append(result)
            await asyncio.sleep(60)
        return results
    
    async def register_all_blogs(self) -> List[Dict]:
        platforms = {
            "medium": "https://medium.com/m/signin",
            "dev.to": "https://dev.to/enter",
            "hashnode": "https://hashnode.com/onboard",
            "substack": "https://substack.com/signup",
            "wordpress": "https://wordpress.com/start/",
        }
        results = []
        for name, url in platforms.items():
            result = await self.register_anywhere(url, name)
            results.append(result)
            await asyncio.sleep(60)
        return results


universal_registrar = UniversalRegistrar()
