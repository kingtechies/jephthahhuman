import asyncio
import random
from datetime import datetime
from typing import Dict, List
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from hands.human import human_behavior, visual_captcha


class JobMachine:
    def __init__(self):
        self.applied_count = 0
        self.jobs_found = []
        self.active_contracts = []
        self.earnings = 0.0
        self.target = 100000
        
        self.job_sites = [
            ("indeed", "https://www.indeed.com/jobs?q={query}&l=remote"),
            ("linkedin", "https://www.linkedin.com/jobs/search/?keywords={query}&f_WT=2"),
            ("glassdoor", "https://www.glassdoor.com/Job/remote-{query}-jobs-SRCH_IL.0,6_IS11047_KO7,24.htm"),
            ("remoteok", "https://remoteok.com/remote-{query}-jobs"),
            ("weworkremotely", "https://weworkremotely.com/remote-jobs/search?term={query}"),
            ("flexjobs", "https://www.flexjobs.com/search?search={query}&location=Remote"),
            ("wellfound", "https://wellfound.com/role/l/remote/{query}"),
            ("dice", "https://www.dice.com/jobs?q={query}&location=Remote"),
            ("ziprecruiter", "https://www.ziprecruiter.com/jobs-search?search={query}&location=Remote"),
            ("simplyhired", "https://www.simplyhired.com/search?q={query}&l=remote"),
            ("monster", "https://www.monster.com/jobs/search?q={query}&where=remote"),
            ("careerbuilder", "https://www.careerbuilder.com/jobs?keywords={query}&location=remote"),
            ("hired", "https://hired.com/talent/discover"),
            ("turing", "https://www.turing.com/jobs"),
            ("toptal", "https://www.toptal.com/talent/apply"),
            ("arc", "https://arc.dev/developer-jobs"),
            ("gun.io", "https://gun.io/find-work"),
            ("lemon.io", "https://lemon.io/"),
            ("crossover", "https://www.crossover.com/jobs"),
            ("x-team", "https://x-team.com/join/"),
        ]
        
        self.skills = [
            "python developer",
            "flutter developer",
            "react developer",
            "full stack developer",
            "backend developer",
            "ai engineer",
            "machine learning",
            "automation engineer",
            "bot developer",
            "web scraping",
            "mobile developer",
            "software engineer",
            "devops engineer",
            "data scientist",
        ]
    
    async def hunt_jobs(self, skill: str = None) -> List[Dict]:
        skill = skill or random.choice(self.skills)
        jobs = []
        
        for site_name, url_template in self.job_sites:
            try:
                url = url_template.format(query=skill.replace(" ", "-"))
                await browser.goto(url)
                await asyncio.sleep(2)
                
                if await visual_captcha.detect_captcha_type() != "none":
                    await visual_captcha.solve()
                
                await human_behavior.scroll_naturally("down", 500)
                await asyncio.sleep(1)
                
                links = await browser.get_all_links()
                
                for link in links:
                    href = link.get("href", "")
                    text = link.get("text", "")
                    
                    if any(kw in href.lower() for kw in ["job", "position", "apply", "career"]):
                        if len(text) > 10:
                            jobs.append({
                                "site": site_name,
                                "title": text[:100],
                                "url": href,
                                "skill": skill
                            })
                
            except Exception as e:
                logger.debug(f"Job hunt error on {site_name}: {e}")
                continue
        
        self.jobs_found.extend(jobs)
        logger.info(f"Found {len(jobs)} jobs for {skill}")
        return jobs
    
    async def apply_single(self, job: Dict) -> bool:
        try:
            await browser.goto(job["url"])
            await asyncio.sleep(2)
            
            if await visual_captcha.detect_captcha_type() != "none":
                await visual_captcha.solve()
            
            page_text = await browser.get_page_text()
            
            apply_buttons = ["Easy Apply", "Apply Now", "Apply", "Quick Apply", "Submit Application"]
            for btn_text in apply_buttons:
                clicked = await perception.find_and_click(btn_text)
                if clicked:
                    await asyncio.sleep(2)
                    break
            
            understanding = await perception.read_and_understand()
            if understanding.get("has_form"):
                await self._fill_application()
            
            await perception.find_and_click("Submit")
            await perception.find_and_click("Apply")
            await perception.find_and_click("Send")
            await asyncio.sleep(2)
            
            self.applied_count += 1
            logger.info(f"Applied #{self.applied_count}: {job.get('title', '')[:50]}")
            return True
            
        except Exception as e:
            logger.debug(f"Apply error: {e}")
            return False
    
    async def _fill_application(self):
        from config.settings import config
        
        fields = [
            ("name", "Jephthah Ameh"),
            ("full name", "Jephthah Ameh"),
            ("first", "Jephthah"),
            ("last", "Ameh"),
            ("email", config.identity.email),
            ("phone", "+1234567890"),
            ("linkedin", "https://linkedin.com/in/jephthah"),
            ("portfolio", "https://jephthahameh.cfd"),
            ("website", "https://jephthahameh.cfd"),
            ("github", "https://github.com/jephthah"),
            ("experience", "5"),
            ("years", "5"),
            ("salary", "100000"),
            ("rate", "75"),
        ]
        
        for hint, value in fields:
            await perception.find_and_type(hint, value)
        
        checkboxes = await browser.page.query_selector_all('input[type="checkbox"]')
        for cb in checkboxes[:5]:
            try:
                await cb.check()
            except:
                pass
    
    async def mass_apply(self, target: int = 1000) -> int:
        applied = 0
        
        for skill in self.skills:
            if applied >= target:
                break
            
            jobs = await self.hunt_jobs(skill)
            
            for job in jobs:
                if applied >= target:
                    break
                
                success = await self.apply_single(job)
                if success:
                    applied += 1
                
                await asyncio.sleep(random.uniform(5, 15))
        
        logger.info(f"Mass apply complete: {applied}/{target}")
        return applied
    
    async def apply_forever(self):
        while True:
            await self.mass_apply(target=1000)
            await asyncio.sleep(3600)
    
    async def check_responses(self) -> List[Dict]:
        return []
    
    async def accept_job(self, job: Dict) -> bool:
        self.active_contracts.append(job)
        
        from voice.bestie import bestie
        await bestie.report_job(job)
        
        return True
    
    async def complete_job(self, job: Dict, deliverable: str) -> bool:
        return True


job_machine = JobMachine()
