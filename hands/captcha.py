"""
Jephthah CAPTCHA Solver
Integration with 2Captcha and Anti-Captcha services
"""

import asyncio
from typing import Optional
import httpx
from loguru import logger

from config.settings import config


class CaptchaSolver:
    """CAPTCHA solving capabilities"""
    
    def __init__(self):
        self.twocaptcha_key = config.captcha.twocaptcha_key
        self.anticaptcha_key = config.captcha.anticaptcha_key
        
        logger.info("CAPTCHA solver initialized")
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2"""
        if not self.twocaptcha_key:
            logger.warning("No 2Captcha API key configured")
            return None
        
        try:
            # Submit CAPTCHA
            async with httpx.AsyncClient() as client:
                # Request solve
                submit_url = "http://2captcha.com/in.php"
                params = {
                    "key": self.twocaptcha_key,
                    "method": "userrecaptcha",
                    "googlekey": site_key,
                    "pageurl": page_url,
                    "json": 1
                }
                
                response = await client.get(submit_url, params=params)
                data = response.json()
                
                if data.get("status") != 1:
                    logger.error(f"CAPTCHA submit failed: {data}")
                    return None
                
                request_id = data.get("request")
                
                # Poll for result
                result_url = "http://2captcha.com/res.php"
                
                for _ in range(30):  # Max 30 attempts (2.5 minutes)
                    await asyncio.sleep(5)
                    
                    result_params = {
                        "key": self.twocaptcha_key,
                        "action": "get",
                        "id": request_id,
                        "json": 1
                    }
                    
                    result = await client.get(result_url, params=result_params)
                    result_data = result.json()
                    
                    if result_data.get("status") == 1:
                        token = result_data.get("request")
                        logger.info("reCAPTCHA solved successfully")
                        return token
                    elif result_data.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        logger.error(f"CAPTCHA solve failed: {result_data}")
                        return None
                
                logger.error("CAPTCHA solve timeout")
                return None
                
        except Exception as e:
            logger.error(f"CAPTCHA solve error: {e}")
            return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCAPTCHA"""
        if not self.twocaptcha_key:
            logger.warning("No 2Captcha API key configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                submit_url = "http://2captcha.com/in.php"
                params = {
                    "key": self.twocaptcha_key,
                    "method": "hcaptcha",
                    "sitekey": site_key,
                    "pageurl": page_url,
                    "json": 1
                }
                
                response = await client.get(submit_url, params=params)
                data = response.json()
                
                if data.get("status") != 1:
                    return None
                
                request_id = data.get("request")
                
                result_url = "http://2captcha.com/res.php"
                
                for _ in range(30):
                    await asyncio.sleep(5)
                    
                    result = await client.get(result_url, params={
                        "key": self.twocaptcha_key,
                        "action": "get",
                        "id": request_id,
                        "json": 1
                    })
                    
                    result_data = result.json()
                    
                    if result_data.get("status") == 1:
                        logger.info("hCAPTCHA solved successfully")
                        return result_data.get("request")
                    elif result_data.get("request") != "CAPCHA_NOT_READY":
                        logger.error(f"hCAPTCHA failed: {result_data}")
                        return None
                
                return None
                
        except Exception as e:
            logger.error(f"hCAPTCHA error: {e}")
            return None
    
    async def solve_image_captcha(self, image_base64: str) -> Optional[str]:
        """Solve image-based CAPTCHA"""
        if not self.twocaptcha_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                submit_url = "http://2captcha.com/in.php"
                
                response = await client.post(submit_url, data={
                    "key": self.twocaptcha_key,
                    "method": "base64",
                    "body": image_base64,
                    "json": 1
                })
                
                data = response.json()
                
                if data.get("status") != 1:
                    return None
                
                request_id = data.get("request")
                
                for _ in range(20):
                    await asyncio.sleep(3)
                    
                    result = await client.get("http://2captcha.com/res.php", params={
                        "key": self.twocaptcha_key,
                        "action": "get",
                        "id": request_id,
                        "json": 1
                    })
                    
                    result_data = result.json()
                    
                    if result_data.get("status") == 1:
                        logger.info("Image CAPTCHA solved")
                        return result_data.get("request")
                    elif result_data.get("request") != "CAPCHA_NOT_READY":
                        return None
                
                return None
                
        except Exception as e:
            logger.error(f"Image CAPTCHA error: {e}")
            return None
    
    def get_balance(self) -> float:
        """Get 2Captcha account balance"""
        if not self.twocaptcha_key:
            return 0.0
        
        try:
            import requests
            response = requests.get(
                "http://2captcha.com/res.php",
                params={
                    "key": self.twocaptcha_key,
                    "action": "getbalance",
                    "json": 1
                }
            )
            data = response.json()
            return float(data.get("request", 0))
        except:
            return 0.0


# Global CAPTCHA solver instance
captcha_solver = CaptchaSolver()
