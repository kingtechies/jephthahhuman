import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.perception import perception
from brain.memory import memory


class JobHunter:
    def __init__(self):
        self.job_boards = {
            "indeed": "https://www.indeed.com/jobs?q={query}",
            "glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}",
            "remoteok": "https://remoteok.com/remote-{query}-jobs",
            "weworkremotely": "https://weworkremotely.com/remote-jobs/search?term={query}",
            "angellist": "https://angel.co/jobs?q={query}",
        }
        self.skills = ["python", "flutter", "react", "ai", "automation", "bot"]
        self.applied_jobs = set()
        
    async def search(self, query: str = "python developer", board: str = "remoteok") -> List[Dict]:
        jobs = []
        url_template = self.job_boards.get(board)
        if not url_template:
            return []
        try:
            url = url_template.format(query=query.replace(" ", "-"))
            await browser.goto(url)
            await asyncio.sleep(3)
            for _ in range(3):
                await browser.scroll_like_human("down", 500)
                await asyncio.sleep(1)
            links = await browser.get_all_links()
            for link in links:
                href = link.get("href", "")
                text = link.get("text", "")
                if any(kw in text.lower() for kw in ["developer", "engineer", "remote"]):
                    jobs.append({"url": href, "title": text[:100], "board": board})
            logger.info(f"Found {len(jobs)} jobs on {board}")
        except Exception as e:
            logger.error(f"Job search error: {e}")
        return jobs[:20]
    
    async def apply(self, job: Dict) -> bool:
        url = job.get("url")
        if not url or url in self.applied_jobs:
            return False
        try:
            await browser.goto(url)
            await asyncio.sleep(2)
            page_text = await browser.get_page_text()
            if "easy apply" in page_text.lower():
                await perception.find_and_click("Easy Apply")
                await asyncio.sleep(2)
            elif "apply" in page_text.lower():
                await perception.find_and_click("Apply")
                await asyncio.sleep(2)
            else:
                return False
            understanding = await perception.read_and_understand()
            if understanding.get("has_form"):
                await self._fill_application()
            self.applied_jobs.add(url)
            memory.log_action("job", "apply", job.get("board", ""), "success", job)
            logger.info(f"Applied: {job.get('title', '')[:50]}")
            return True
        except Exception as e:
            logger.error(f"Job apply error: {e}")
            return False
    
    async def _fill_application(self):
        await perception.find_and_type("name", "Jephthah Ameh")
        await perception.find_and_type("email", config.identity.email)
        await perception.find_and_type("phone", "+1234567890")
        await perception.find_and_type("linkedin", "https://linkedin.com/in/jephthah")
        await perception.find_and_type("portfolio", "https://jephthahameh.cfd")
        checkboxes = await browser.page.query_selector_all('input[type="checkbox"]')
        for cb in checkboxes[:3]:
            try:
                await cb.check()
            except:
                pass
        await perception.find_and_click("Submit")
        await perception.find_and_click("Apply")
    
    async def mass_apply(self, target: int = 100) -> int:
        applied = 0
        for skill in self.skills:
            if applied >= target:
                break
            for board in self.job_boards.keys():
                if applied >= target:
                    break
                jobs = await self.search(skill, board)
                for job in jobs:
                    if applied >= target:
                        break
                    success = await self.apply(job)
                    if success:
                        applied += 1
                    await asyncio.sleep(random.uniform(30, 60))
        logger.info(f"Mass apply complete: {applied}/{target}")
        return applied


class FiverrBot:
    def __init__(self):
        self.base_url = "https://www.fiverr.com"
        self.logged_in = False
        
    async def login(self) -> bool:
        if self.logged_in:
            return True
        email = config.freelance.fiverr_email
        password = config.freelance.fiverr_password
        if not email or not password:
            return False
        try:
            await browser.goto(f"{self.base_url}/login")
            await asyncio.sleep(2)
            await perception.find_and_type("email", email)
            await perception.find_and_click("Continue")
            await asyncio.sleep(1)
            await perception.find_and_type("password", password)
            await perception.find_and_click("Continue")
            await asyncio.sleep(3)
            self.logged_in = True
            return True
        except:
            return False
    
    async def create_gig(self, title: str, description: str, price: int = 50) -> bool:
        if not await self.login():
            return False
        try:
            await browser.goto(f"{self.base_url}/users/seller_dashboard")
            await asyncio.sleep(2)
            await perception.find_and_click("Create a New Gig")
            await asyncio.sleep(2)
            await perception.find_and_type("title", title)
            await perception.find_and_click("Save & Continue")
            await asyncio.sleep(2)
            return True
        except:
            return False
    
    async def check_orders(self) -> List[Dict]:
        if not await self.login():
            return []
        try:
            await browser.goto(f"{self.base_url}/users/seller_dashboard/orders")
            await asyncio.sleep(2)
            return []
        except:
            return []


job_hunter = JobHunter()
fiverr = FiverrBot()
