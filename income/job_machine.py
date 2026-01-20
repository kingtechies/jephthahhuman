"""
Jephthah Job Machine
Advanced job hunting, applications, and tracking with Telegram notifications
"""

import asyncio
import random
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from hands.human import human_behavior, visual_captcha
from config.settings import DATA_DIR


class JobMachine:
    """Advanced job hunting with retry logic and notifications"""
    
    def __init__(self):
        self.applied_count = 0
        self.jobs_found: List[Dict] = []
        self.applications_history: List[Dict] = []
        self.active_contracts = []
        self.earnings = 0.0
        self.target = 100000
        self.db_path = DATA_DIR / "job_applications.json"
        
        # Load existing applications
        self._load_history()
        
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
    
    def _load_history(self):
        """Load application history from disk"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.applications_history = data.get("applications", [])
                    self.applied_count = len(self.applications_history)
                    logger.info(f"📂 Loaded {self.applied_count} previous applications")
        except Exception as e:
            logger.error(f"Error loading job history: {e}")
            self.applications_history = []
    
    def _save_history(self):
        """Save application history to disk"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump({
                    "applications": self.applications_history,
                    "updated": datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving job history: {e}")
    
    async def hunt_jobs(self, skill: str = None, max_sites: int = 5) -> List[Dict]:
        """Hunt for jobs with retry logic"""
        skill = skill or random.choice(self.skills)
        jobs = []
        sites_to_check = random.sample(self.job_sites, min(max_sites, len(self.job_sites)))
        
        for site_name, url_template in sites_to_check:
            try:
                url = url_template.format(query=skill.replace(" ", "-"))
                success = await browser.goto_safe(url)
                
                if not success:
                    continue
                
                await asyncio.sleep(2)
                
                # Check for captcha
                captcha_type = await visual_captcha.detect_captcha_type()
                if captcha_type != "none":
                    solved = await visual_captcha.solve()
                    if not solved:
                        continue
                
                await human_behavior.scroll_naturally("down", 500)
                await asyncio.sleep(1)
                
                # Get page text for job details
                page_text = await browser.get_page_text()
                links = await browser.get_all_links()
                
                for link in links:
                    href = link.get("href", "")
                    text = link.get("text", "").strip()
                    
                    if any(kw in href.lower() for kw in ["job", "position", "apply", "career"]):
                        if len(text) > 10 and len(text) < 200:
                            job = {
                                "site": site_name,
                                "title": text[:100],
                                "url": href,
                                "skill": skill,
                                "found_at": datetime.utcnow().isoformat(),
                                "company": self._extract_company(text, page_text),
                                "salary": self._extract_salary(page_text),
                                "location": "Remote",
                                "description": self._extract_description(page_text)[:500]
                            }
                            jobs.append(job)
                
                logger.info(f"🔍 Found {len([j for j in jobs if j['site'] == site_name])} jobs on {site_name}")
                
            except Exception as e:
                logger.debug(f"Job hunt error on {site_name}: {e}")
                continue
        
        self.jobs_found.extend(jobs)
        logger.info(f"🎯 Total found: {len(jobs)} jobs for '{skill}'")
        return jobs
    
    def _extract_company(self, title: str, page_text: str) -> str:
        """Try to extract company name"""
        # Common patterns: "Title at Company", "Title - Company"
        if " at " in title:
            return title.split(" at ")[-1].strip()[:50]
        if " - " in title:
            parts = title.split(" - ")
            if len(parts) > 1:
                return parts[-1].strip()[:50]
        return "Unknown Company"
    
    def _extract_salary(self, page_text: str) -> str:
        """Try to extract salary from page"""
        import re
        patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',  # $80,000 - $120,000
            r'\$[\d,]+k?\s*-\s*\$?[\d,]+k?',  # $80k - $120k
            r'\$[\d,]+\s*(?:per\s+)?(?:year|yr|annual)',  # $100,000 per year
        ]
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group()[:50]
        return "Not specified"
    
    def _extract_description(self, page_text: str) -> str:
        """Extract job description snippet"""
        # Get first ~500 chars of meaningful content
        lines = page_text.split('\n')
        description = []
        for line in lines:
            line = line.strip()
            if len(line) > 50 and len(line) < 500:
                description.append(line)
            if len(' '.join(description)) > 500:
                break
        return ' '.join(description)[:500] if description else "No description available"
    
    async def apply_single(self, job: Dict, notify: bool = True) -> bool:
        """Apply to a single job with retry"""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                success = await browser.goto_safe(job["url"])
                if not success:
                    continue
                
                await asyncio.sleep(2)
                
                # Check for captcha
                captcha_type = await visual_captcha.detect_captcha_type()
                if captcha_type != "none":
                    await visual_captcha.solve()
                
                page_text = await browser.get_page_text()
                
                # Update job with more details from job page
                job["description"] = self._extract_description(page_text)
                job["salary"] = self._extract_salary(page_text)
                
                # Try different apply buttons
                apply_buttons = ["Easy Apply", "Apply Now", "Apply", "Quick Apply", "Submit Application", "Apply for this job"]
                clicked = False
                for btn_text in apply_buttons:
                    if await browser.click_text_safe(btn_text):
                        clicked = True
                        await asyncio.sleep(2)
                        break
                
                if not clicked:
                    # Try to find any apply-like link
                    links = await browser.get_all_links()
                    for link in links:
                        if "apply" in link.get("text", "").lower():
                            await browser.goto_safe(link.get("href", ""))
                            clicked = True
                            break
                
                # Check if there's a form
                understanding = await perception.read_and_understand()
                if understanding.get("has_form"):
                    await self._fill_application()
                
                # Try to submit
                for submit_text in ["Submit", "Apply", "Send", "Submit Application", "Complete"]:
                    await browser.click_text_safe(submit_text)
                
                await asyncio.sleep(2)
                
                # Record application
                application = {
                    **job,
                    "applied_at": datetime.utcnow().isoformat(),
                    "status": "applied"
                }
                self.applications_history.append(application)
                self.applied_count += 1
                self._save_history()
                
                logger.info(f"✅ Applied #{self.applied_count}: {job.get('title', '')[:50]} at {job.get('company', 'Unknown')}")
                
                # Send Telegram notification
                if notify:
                    await self._notify_application(application)
                
                return True
                
            except Exception as e:
                logger.warning(f"Apply attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                continue
        
        logger.debug(f"❌ Failed to apply: {job.get('title', '')[:50]}")
        return False
    
    async def _fill_application(self):
        """Fill out job application form"""
        from config.settings import config
        
        fields = [
            ("name", "Jephthah Ameh"),
            ("full name", "Jephthah Ameh"),
            ("first", "Jephthah"),
            ("last", "Ameh"),
            ("email", config.identity.email),
            ("phone", "+2348123456789"),
            ("linkedin", "https://linkedin.com/in/jephthah-ameh"),
            ("portfolio", config.identity.website),
            ("website", config.identity.website),
            ("github", f"https://github.com/{config.infra.github_username}"),
            ("experience", "5"),
            ("years", "5"),
            ("salary", "100000"),
            ("rate", "75"),
            ("cover", "I am a passionate software engineer with 5+ years of experience in Python, AI, and web development."),
        ]
        
        for hint, value in fields:
            try:
                await perception.find_and_type(hint, value)
            except:
                pass
        
        # Check checkboxes (terms, etc)
        try:
            checkboxes = await browser.page.query_selector_all('input[type="checkbox"]')
            for cb in checkboxes[:5]:
                try:
                    await cb.check()
                except:
                    pass
        except:
            pass
    
    async def _notify_application(self, job: Dict):
        """Send detailed Telegram notification for job application"""
        try:
            from voice.bestie import bestie
            
            msg = f"""🎯 **JOB APPLIED** #{self.applied_count}

📌 **Title**: {job.get('title', 'Unknown')[:60]}
🏢 **Company**: {job.get('company', 'Unknown')}
📍 **Location**: {job.get('location', 'Remote')}
💰 **Salary**: {job.get('salary', 'Not specified')}
🌐 **Site**: {job.get('site', 'Unknown')}

📝 **Description**:
{job.get('description', 'N/A')[:300]}...

🔗 [View Job]({job.get('url', '#')})

⏰ Applied at: {job.get('applied_at', datetime.utcnow().isoformat())[:19]}"""
            
            await bestie.send(msg)
            
        except Exception as e:
            logger.debug(f"Notification error: {e}")
    
    async def mass_apply(self, target: int = 1000, notify: bool = True) -> int:
        """Mass apply to jobs with progress tracking"""
        applied = 0
        
        for skill in self.skills:
            if applied >= target:
                break
            
            jobs = await self.hunt_jobs(skill, max_sites=3)
            
            for job in jobs:
                if applied >= target:
                    break
                
                # Skip if already applied to this URL
                if any(app.get("url") == job.get("url") for app in self.applications_history):
                    continue
                
                success = await self.apply_single(job, notify=notify)
                if success:
                    applied += 1
                
                # Random delay between applications (5-15 seconds)
                await asyncio.sleep(random.uniform(5, 15))
        
        logger.info(f"🎯 Mass apply complete: {applied}/{target}")
        return applied
    
    async def apply_forever(self, daily_target: int = 50):
        """Continuous job application loop"""
        while True:
            await self.mass_apply(target=daily_target)
            # Wait 1 hour before next batch
            await asyncio.sleep(3600)
    
    def get_stats(self) -> Dict:
        """Get application statistics"""
        today = datetime.utcnow().date().isoformat()
        today_apps = [a for a in self.applications_history if a.get("applied_at", "").startswith(today)]
        
        return {
            "total_applied": self.applied_count,
            "today_applied": len(today_apps),
            "jobs_found": len(self.jobs_found),
            "applications": self.applications_history[-10:],  # Last 10
            "by_site": self._count_by_site(),
            "by_skill": self._count_by_skill(),
        }
    
    def _count_by_site(self) -> Dict[str, int]:
        """Count applications by site"""
        counts = {}
        for app in self.applications_history:
            site = app.get("site", "unknown")
            counts[site] = counts.get(site, 0) + 1
        return counts
    
    def _count_by_skill(self) -> Dict[str, int]:
        """Count applications by skill"""
        counts = {}
        for app in self.applications_history:
            skill = app.get("skill", "unknown")
            counts[skill] = counts.get(skill, 0) + 1
        return counts
    
    async def check_responses(self) -> List[Dict]:
        """Check for job responses (placeholder for future)"""
        return []
    
    async def accept_job(self, job: Dict) -> bool:
        """Accept a job offer"""
        self.active_contracts.append(job)
        
        from voice.bestie import bestie
        await bestie.report_job(job)
        
        return True
    
    async def complete_job(self, job: Dict, deliverable: str) -> bool:
        """Complete a job"""
        return True


# Global job machine instance
job_machine = JobMachine()
