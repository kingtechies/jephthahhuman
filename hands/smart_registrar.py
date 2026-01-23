import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from hands.human import visual_captcha
from voice.otp_handler import otp_handler


class SmartRegistrar:
    def __init__(self):
        self.email = "hireme@jephthahameh.cfd"
        self.registered = {}
        self.phone_number = None
        
        self.platforms = {
            "github": {"url": "https://github.com/signup", "phone": "optional"},
            "linkedin": {"url": "https://www.linkedin.com/signup", "phone": "optional"},
            "medium": {"url": "https://medium.com/m/signin", "phone": "never"},
            "dev.to": {"url": "https://dev.to/enter", "phone": "never"},
            "hashnode": {"url": "https://hashnode.com/onboard", "phone": "never"},
            "upwork": {"url": "https://www.upwork.com/nx/signup/", "phone": "optional"},
            "fiverr": {"url": "https://www.fiverr.com/join", "phone": "optional"},
            "freelancer": {"url": "https://www.freelancer.com/signup", "phone": "optional"},
            "reddit": {"url": "https://www.reddit.com/register/", "phone": "never"},
            "substack": {"url": "https://substack.com/signup", "phone": "never"},
            "gumroad": {"url": "https://gumroad.com/signup", "phone": "never"},
            "producthunt": {"url": "https://www.producthunt.com/", "phone": "never"},
            "twitter": {"url": "https://x.com/i/flow/signup", "phone": "required"},
            "facebook": {"url": "https://www.facebook.com/r.php", "phone": "required"},
            "instagram": {"url": "https://www.instagram.com/accounts/emailsignup/", "phone": "required"},
            "tiktok": {"url": "https://www.tiktok.com/signup", "phone": "required"},
        }
        
        self.priority_order = [
            "github", "linkedin", "medium", "dev.to", "upwork", "fiverr",
            "freelancer", "hashnode", "reddit", "substack", "gumroad", "producthunt",
            "twitter", "facebook", "instagram"
        ]
    
    async def register(self, platform: str) -> Dict:
        """Register on a known platform by name"""
        info = self.platforms.get(platform)
        if not info:
            return {"platform": platform, "status": "unknown"}
        
        url = info["url"]
        phone_req = info["phone"]
        
        if phone_req == "required" and not self.phone_number:
            self.phone_number = await self._ask_for_phone(platform)
            if not self.phone_number:
                return {"platform": platform, "status": "pending_phone"}
        
        return await self._do_register(platform, url, phone_req)
    
    async def register_url(self, platform: str, url: str) -> Dict:
        """Register on any URL with given platform name"""
        return await self._do_register(platform, url, "never")
    
    async def _ask_for_phone(self, platform: str) -> Optional[str]:
        from voice.bestie import bestie
        
        await bestie.send(
            f"Hey bestie! I need your phone to register on {platform}.\n"
            f"Send as: phone: +1234567890"
        )
        
        return await bestie.ask_for_phone()
    
    async def _do_register(self, platform: str, url: str, phone_req: str) -> Dict:
        result = {"platform": platform, "status": "pending"}
        
        try:
            await browser.goto(url)
            await asyncio.sleep(2)
            
            if await visual_captcha.detect_captcha_type() != "none":
                await visual_captcha.solve()
            
            password = self._gen_password()
            username = f"jephthah{datetime.utcnow().strftime('%m%d%H%M')}"
            
            await self._fill_form(username, password, phone_req)
            await self._submit()
            await asyncio.sleep(3)
            
            if await visual_captcha.detect_captcha_type() != "none":
                await visual_captcha.solve()
            
            page_text = await browser.get_page_text()
            
            if any(w in page_text.lower() for w in ["verify email", "check your email", "verification email"]):
                otp = await otp_handler.check_for_otp(timeout=120)
                if otp:
                    await perception.find_and_type("code", otp)
                    await perception.find_and_type("otp", otp)
                    await self._submit()
            
            elif any(w in page_text.lower() for w in ["verify phone", "sms", "text message"]):
                from voice.bestie import bestie
                await bestie.send(f"Need SMS OTP for {platform}. Send as: otp: XXXXXX")
                sms_otp = await bestie.ask_for_otp(platform)
                if sms_otp:
                    await perception.find_and_type("code", sms_otp)
                    await self._submit()
            
            page_text = await browser.get_page_text()
            if any(w in page_text.lower() for w in ["welcome", "success", "dashboard", "profile", "home"]):
                result["status"] = "success"
                result["username"] = username
                self.registered[platform] = result
                
                from config.settings import config
                config.save_credential(f"{platform.upper()}_USERNAME", username)
                config.save_credential(f"{platform.upper()}_PASSWORD", password)
                
                from voice.bestie import bestie
                await bestie.share_win(f"Registered on {platform}! Username: {username}")
                
                logger.info(f"Registered on {platform}: {username}")
            else:
                result["status"] = "uncertain"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result
    
    async def _fill_form(self, username: str, password: str, phone_req: str):
        fields = [
            ("email", self.email),
            ("e-mail", self.email),
            ("username", username),
            ("user", username),
            ("name", "Jephthah Ameh"),
            ("fullname", "Jephthah Ameh"),
            ("first", "Jephthah"),
            ("last", "Ameh"),
            ("password", password),
            ("confirm", password),
        ]
        
        if phone_req in ["required", "optional"] and self.phone_number:
            fields.append(("phone", self.phone_number))
            fields.append(("mobile", self.phone_number))
        
        for hint, value in fields:
            await perception.find_and_type(hint, value)
        
        for cb in await browser.page.query_selector_all('input[type="checkbox"]'):
            try:
                await cb.check()
            except:
                pass
    
    async def _submit(self):
        buttons = ["Sign up", "Register", "Create", "Continue", "Next", "Submit", "Join", "Get started"]
        for btn in buttons:
            if await perception.find_and_click(btn):
                await asyncio.sleep(2)
                return
        try:
            await browser.click_like_human('button[type="submit"]')
        except:
            pass
    
    def _gen_password(self) -> str:
        import random
        chars = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789!@#$"
        return "Jeph" + ''.join(random.choices(chars, k=12))
    
    async def register_all(self) -> List[Dict]:
        results = []
        for platform in self.priority_order:
            result = await self.register(platform)
            results.append(result)
            await asyncio.sleep(30)
        return results
    
    async def register_email_only(self) -> List[Dict]:
        results = []
        for platform, info in self.platforms.items():
            if info["phone"] == "never":
                result = await self.register(platform)
                results.append(result)
                await asyncio.sleep(30)
        return results
    
    async def register_ai_platforms(self) -> List[Dict]:
        ai_platforms = {
            "perplexity": "https://www.perplexity.ai/signup",
            "phind": "https://www.phind.com/",
            "you": "https://you.com/",
            "poe": "https://poe.com/login",
            "chatgpt": "https://chat.openai.com",
            "gemini": "https://gemini.google.com",
        }
        results = []
        for name, url in ai_platforms.items():
            result = await self._do_register(name, url, "never")
            results.append(result)
            await asyncio.sleep(30)
        return results


smart_registrar = SmartRegistrar()
