"""
Jephthah LinkedIn Automation
Professional networking and job hunting
"""

import asyncio
import random
from typing import List, Dict, Optional
from datetime import datetime

from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.vision import vision
from brain.memory import memory


class LinkedInBot:
    """LinkedIn automation for networking and jobs"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com"
        self.logged_in = False
        
    async def login(self) -> bool:
        """Login to LinkedIn"""
        if self.logged_in:
            return True
        
        email = config.social.linkedin_email
        password = config.social.linkedin_password
        
        if not email or not password:
            logger.warning("LinkedIn credentials not configured")
            return False
        
        try:
            await browser.goto("https://www.linkedin.com/login")
            await asyncio.sleep(2)
            
            await browser.type_like_human('#username', email)
            await browser.type_like_human('#password', password)
            await browser.click_like_human('button[type="submit"]')
            await asyncio.sleep(3)
            
            if await vision.is_logged_in(["Feed", "My Network", "Jobs"]):
                self.logged_in = True
                logger.info("LinkedIn login successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"LinkedIn login error: {e}")
            return False
    
    async def search_jobs(self, query: str, location: str = "Remote") -> List[Dict]:
        """Search for jobs"""
        if not await self.login():
            return []
        
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"
            await browser.goto(url)
            await asyncio.sleep(3)
            
            links = await browser.get_all_links()
            job_links = [l for l in links if "/jobs/view/" in l.get("href", "")][:20]
            
            return job_links
            
        except Exception as e:
            logger.error(f"LinkedIn job search error: {e}")
            return []
    
    async def apply_easy_apply(self, job_url: str) -> bool:
        """Apply using Easy Apply"""
        try:
            await browser.goto(job_url)
            await asyncio.sleep(2)
            
            easy_apply = await browser.wait_for_selector('button:has-text("Easy Apply")', timeout=5000)
            if not easy_apply:
                return False
            
            await browser.click_like_human('button:has-text("Easy Apply")')
            await asyncio.sleep(2)
            
            # Follow the apply flow
            for _ in range(5):  # Max 5 steps
                submit = await browser.wait_for_selector('button:has-text("Submit application")', timeout=2000)
                if submit:
                    await browser.click_like_human('button:has-text("Submit application")')
                    logger.info(f"Applied to job: {job_url}")
                    return True
                
                next_btn = await browser.wait_for_selector('button:has-text("Next")', timeout=2000)
                if next_btn:
                    await browser.click_like_human('button:has-text("Next")')
                    await asyncio.sleep(1)
                else:
                    break
            
            return False
            
        except Exception as e:
            logger.error(f"Easy Apply error: {e}")
            return False
    
    async def connect_with(self, profile_url: str, note: str = None) -> bool:
        """Send connection request"""
        try:
            await browser.goto(profile_url)
            await asyncio.sleep(2)
            
            await browser.click_like_human('button:has-text("Connect")')
            await asyncio.sleep(1)
            
            if note:
                add_note = await browser.wait_for_selector('button:has-text("Add a note")', timeout=2000)
                if add_note:
                    await browser.click_like_human('button:has-text("Add a note")')
                    await browser.type_like_human('textarea[name="message"]', note)
            
            await browser.click_like_human('button:has-text("Send")')
            logger.info(f"Connection request sent: {profile_url}")
            return True
            
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return False
    
    async def post_update(self, content: str) -> bool:
        """Post a LinkedIn update"""
        try:
            await browser.goto("https://www.linkedin.com/feed/")
            await asyncio.sleep(2)
            
            await browser.click_like_human('button:has-text("Start a post")')
            await asyncio.sleep(1)
            
            await browser.type_like_human('[role="textbox"]', content)
            await asyncio.sleep(1)
            
            await browser.click_like_human('button:has-text("Post")')
            logger.info("LinkedIn post published")
            return True
            
        except Exception as e:
            logger.error(f"Post error: {e}")
            return False


# Global LinkedIn bot
linkedin = LinkedInBot()
