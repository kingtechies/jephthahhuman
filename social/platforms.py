import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.perception import perception
from brain.autonomous import brain
from brain.memory import memory


class InstagramBot:
    def __init__(self):
        self.base_url = "https://www.instagram.com"
        self.logged_in = False
        
    async def login(self) -> bool:
        if self.logged_in:
            return True
        username = config.social.instagram_username
        password = config.social.instagram_password
        if not username or not password:
            return False
        try:
            await browser.goto(f"{self.base_url}/accounts/login/")
            await asyncio.sleep(2)
            await perception.find_and_type("username", username)
            await perception.find_and_type("password", password)
            await perception.find_and_click("Log in")
            await asyncio.sleep(3)
            self.logged_in = True
            return True
        except Exception as e:
            logger.error(f"Instagram login: {e}")
            return False
    
    async def post(self, caption: str, image_path: str = None) -> bool:
        if not await self.login():
            return False
        try:
            await browser.goto(self.base_url)
            await asyncio.sleep(2)
            await perception.find_and_click("Create")
            await asyncio.sleep(1)
            if image_path:
                file_input = await browser.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
            await asyncio.sleep(2)
            await perception.find_and_click("Next")
            await asyncio.sleep(1)
            await perception.find_and_click("Next")
            await asyncio.sleep(1)
            await perception.find_and_type("caption", caption)
            await perception.find_and_click("Share")
            await asyncio.sleep(3)
            logger.info("Instagram post published")
            return True
        except Exception as e:
            logger.error(f"Instagram post: {e}")
            return False
    
    async def follow(self, username: str) -> bool:
        try:
            await browser.goto(f"{self.base_url}/{username}/")
            await asyncio.sleep(2)
            await perception.find_and_click("Follow")
            await asyncio.sleep(1)
            return True
        except:
            return False
    
    async def like_posts(self, hashtag: str, count: int = 10) -> int:
        liked = 0
        try:
            await browser.goto(f"{self.base_url}/explore/tags/{hashtag}/")
            await asyncio.sleep(3)
            posts = await browser.page.query_selector_all('article a')
            for post in posts[:count]:
                await post.click()
                await asyncio.sleep(1)
                await perception.find_and_click("Like")
                liked += 1
                await asyncio.sleep(random.uniform(2, 5))
                await browser.page.keyboard.press("Escape")
        except Exception as e:
            logger.error(f"Instagram like: {e}")
        return liked


class FacebookBot:
    def __init__(self):
        self.base_url = "https://www.facebook.com"
        self.logged_in = False
        
    async def login(self) -> bool:
        if self.logged_in:
            return True
        email = config.social.facebook_email
        password = config.social.facebook_password
        if not email or not password:
            return False
        try:
            await browser.goto(self.base_url)
            await asyncio.sleep(2)
            await perception.find_and_type("email", email)
            await perception.find_and_type("pass", password)
            await perception.find_and_click("Log In")
            await asyncio.sleep(3)
            self.logged_in = True
            return True
        except Exception as e:
            logger.error(f"Facebook login: {e}")
            return False
    
    async def post(self, content: str) -> bool:
        if not await self.login():
            return False
        try:
            await browser.goto(self.base_url)
            await asyncio.sleep(2)
            await perception.find_and_click("What's on your mind")
            await asyncio.sleep(1)
            await browser.type_like_human('[role="textbox"]', content)
            await perception.find_and_click("Post")
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Facebook post: {e}")
            return False


class TikTokBot:
    def __init__(self):
        self.base_url = "https://www.tiktok.com"
        self.logged_in = False
        
    async def login(self) -> bool:
        if self.logged_in:
            return True
        try:
            await browser.goto(f"{self.base_url}/login")
            await asyncio.sleep(2)
            return False
        except:
            return False
    
    async def watch_and_engage(self, duration_minutes: int = 30):
        await browser.goto(self.base_url)
        end_time = datetime.utcnow().timestamp() + (duration_minutes * 60)
        while datetime.utcnow().timestamp() < end_time:
            await asyncio.sleep(random.uniform(5, 15))
            if random.random() > 0.5:
                await perception.find_and_click("Like")
            await browser.page.keyboard.press("ArrowDown")


instagram = InstagramBot()
facebook = FacebookBot()
tiktok = TikTokBot()
