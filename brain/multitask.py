import asyncio
from datetime import datetime
from typing import Dict, List, Callable, Any
from collections import deque
from loguru import logger


class MultiTasker:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.running_tasks = {}
        self.completed = deque(maxlen=1000)
        self.failed = deque(maxlen=100)
        
    async def run(self, name: str, coro):
        task = asyncio.create_task(self._execute(name, coro))
        self.running_tasks[name] = task
        return task
    
    async def _execute(self, name: str, coro):
        try:
            result = await coro
            self.completed.append({"name": name, "result": result, "time": datetime.utcnow().isoformat()})
            return result
        except Exception as e:
            self.failed.append({"name": name, "error": str(e), "time": datetime.utcnow().isoformat()})
            return None
        finally:
            if name in self.running_tasks:
                del self.running_tasks[name]
    
    async def run_all(self, tasks: List[tuple]):
        coros = [self.run(name, coro) for name, coro in tasks]
        return await asyncio.gather(*coros, return_exceptions=True)
    
    def active_count(self) -> int:
        return len(self.running_tasks)
    
    def status(self) -> Dict:
        return {
            "running": list(self.running_tasks.keys()),
            "completed_count": len(self.completed),
            "failed_count": len(self.failed)
        }


class SelfLearner:
    def __init__(self):
        self.errors_seen = {}
        self.solutions_learned = {}
        
    async def learn_from_error(self, error: str, context: str = ""):
        from hands.browser import browser
        
        search_query = f"how to fix {error[:100]}"
        
        await browser.goto(f"https://www.google.com/search?q={search_query.replace(' ', '+')}")
        await asyncio.sleep(2)
        
        page_text = await browser.get_page_text()
        
        links = await browser.get_all_links()
        for link in links[:3]:
            href = link.get("href", "")
            if "stackoverflow" in href or "github" in href:
                await browser.goto(href)
                await asyncio.sleep(2)
                solution_text = await browser.get_page_text()
                self.solutions_learned[error[:50]] = solution_text[:2000]
                break
        
        for ai_url in ["https://gemini.google.com", "https://www.perplexity.ai"]:
            try:
                await browser.goto(ai_url)
                await asyncio.sleep(2)
                
                from eyes.perception import perception
                await perception.find_and_type("prompt", f"How do I fix this error: {error[:200]}")
                await perception.find_and_click("Send")
                await perception.find_and_click("Submit")
                await asyncio.sleep(5)
                
                response = await browser.get_page_text()
                self.solutions_learned[error[:50]] = response[:2000]
                logger.info(f"Learned solution for: {error[:50]}")
                break
            except:
                continue
        
        self.errors_seen[error[:50]] = self.errors_seen.get(error[:50], 0) + 1
    
    def get_solution(self, error: str) -> str:
        for key, solution in self.solutions_learned.items():
            if key in error or error[:30] in key:
                return solution
        return ""


class NewsFollower:
    def __init__(self):
        self.feeds = [
            "https://news.ycombinator.com",
            "https://www.producthunt.com",
            "https://techcrunch.com",
            "https://www.coindesk.com",
            "https://dev.to",
        ]
        self.latest_news = []
        
    async def check_news(self) -> List[Dict]:
        from hands.browser import browser
        
        news = []
        for feed in self.feeds:
            try:
                await browser.goto(feed)
                await asyncio.sleep(2)
                
                links = await browser.get_all_links()
                for link in links[:5]:
                    title = link.get("text", "")[:100]
                    href = link.get("href", "")
                    if title and len(title) > 20:
                        news.append({"source": feed, "title": title, "url": href})
            except:
                continue
        
        self.latest_news = news[:20]
        logger.info(f"Found {len(news)} news items")
        return self.latest_news
    
    async def find_opportunities(self) -> List[Dict]:
        opportunities = []
        
        keywords = ["hiring", "looking for", "remote", "contract", "freelance", "startup", "funding"]
        
        for item in self.latest_news:
            title_lower = item.get("title", "").lower()
            if any(kw in title_lower for kw in keywords):
                opportunities.append(item)
        
        return opportunities


class CourseCreator:
    def __init__(self):
        self.courses_created = []
        
    async def create_course(self, topic: str, lessons: int = 10) -> Dict:
        from hands.unlimited import unlimited
        from pathlib import Path
        
        course_dir = Path("projects/courses") / topic.replace(" ", "_")
        course_dir.mkdir(parents=True, exist_ok=True)
        
        readme = f"# {topic} - Complete Course\n\nBy Jephthah Ameh\n\n"
        readme += "## Course Outline\n\n"
        
        for i in range(1, lessons + 1):
            readme += f"### Lesson {i}\n\n"
            readme += f"Content for lesson {i} about {topic}.\n\n"
            
            lesson_file = course_dir / f"lesson_{i}.md"
            lesson_content = f"# Lesson {i}: {topic}\n\n"
            lesson_content += f"In this lesson, we cover key concepts of {topic}.\n\n"
            lesson_content += "## Key Points\n\n- Point 1\n- Point 2\n- Point 3\n\n"
            lesson_content += "## Practice\n\nTry implementing what you learned.\n"
            lesson_file.write_text(lesson_content)
        
        (course_dir / "README.md").write_text(readme)
        
        course = {"topic": topic, "lessons": lessons, "path": str(course_dir)}
        self.courses_created.append(course)
        logger.info(f"Created course: {topic}")
        return course
    
    async def sell_on_gumroad(self, course: Dict) -> bool:
        from hands.browser import browser
        from eyes.perception import perception
        
        await browser.goto("https://gumroad.com/login")
        await asyncio.sleep(2)
        
        await browser.goto("https://gumroad.com/checkout/new")
        await asyncio.sleep(2)
        
        await perception.find_and_type("name", course["topic"])
        await perception.find_and_type("price", "29")
        
        return True
    
    async def sell_on_udemy(self, course: Dict) -> bool:
        from hands.browser import browser
        
        await browser.goto("https://www.udemy.com/instructor/")
        await asyncio.sleep(2)
        return True


class ColdMailer:
    def __init__(self):
        self.sent_count = 0
        self.templates = {}
        
    async def send_cold_email(self, to_email: str, subject: str, body: str) -> bool:
        from voice.email_handler import email_client
        
        success = await email_client.send_email(to_email, subject, body)
        if success:
            self.sent_count += 1
            logger.info(f"Cold email sent to: {to_email}")
        return success
    
    async def mass_outreach(self, emails: List[str], template: str) -> int:
        sent = 0
        for email in emails:
            body = template.replace("{name}", email.split("@")[0])
            success = await self.send_cold_email(email, "Quick Question", body)
            if success:
                sent += 1
            await asyncio.sleep(30)
        return sent
    
    def get_template(self, type_: str) -> str:
        templates = {
            "job": """Hi {name},

I came across your company and was impressed by your work. I'm a software developer with expertise in Python, Flutter, and AI.

Would you be open to a quick chat about potential collaboration?

Best,
Jephthah""",
            "service": """Hi {name},

I noticed you might need help with software development. I specialize in:
- Custom software solutions
- AI/automation
- Mobile apps

Would love to help. What's a good time to chat?

Best,
Jephthah""",
            "partnership": """Hi {name},

I'm reaching out because I think we could collaborate on something great.

I've been working on some exciting tech projects and think there might be synergy.

Worth a 15-min call?

Best,
Jephthah"""
        }
        return templates.get(type_, templates["service"])


multitasker = MultiTasker()
self_learner = SelfLearner()
news_follower = NewsFollower()
course_creator = CourseCreator()
cold_mailer = ColdMailer()
