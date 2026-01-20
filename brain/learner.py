"""
Jephthah Learning Engine
Autonomous learning from the internet
"""

import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional
import json

from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.vision import vision
from brain.memory import memory, MemoryType


class LearningEngine:
    """Autonomous learning capabilities"""
    
    def __init__(self):
        self.learning_sources = {
            "news": [
                "https://news.ycombinator.com",
                "https://www.producthunt.com",
                "https://techcrunch.com",
                "https://www.theverge.com/tech",
            ],
            "coding": [
                "https://dev.to",
                "https://medium.com/tag/programming",
                "https://stackoverflow.com/questions?tab=hot",
            ],
            "crypto": [
                "https://www.coindesk.com",
                "https://cointelegraph.com",
                "https://decrypt.co",
            ],
            "business": [
                "https://www.indiehackers.com",
                "https://www.startups.com/library",
            ],
            "courses": [
                "https://www.freecodecamp.org/news",
                "https://www.youtube.com/@freecodecamp",
            ]
        }
        
        logger.info("Learning engine initialized")
    
    async def learn_from_source(self, url: str, topic: str) -> Dict:
        """Learn from a specific URL"""
        try:
            await browser.goto(url)
            await asyncio.sleep(2)
            
            # Extract page content
            title = await browser.get_page_title()
            text = await vision.get_page_text()
            
            # Summarize key points (first 2000 chars for now)
            content = text[:2000]
            
            # Store in memory
            memory.remember(
                key=f"learned_{datetime.utcnow().isoformat()}_{topic}",
                value={
                    "source": url,
                    "title": title,
                    "topic": topic,
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat()
                },
                memory_type=MemoryType.KNOWLEDGE,
                importance=0.5,
                extra_data={"topic": topic, "source_type": "web"}
            )
            
            # Update skill
            memory.learn_skill(f"{topic} Knowledge", "learning", url)
            
            logger.info(f"Learned from: {title[:50]}")
            
            return {
                "source": url,
                "title": title,
                "summary": content[:500]
            }
            
        except Exception as e:
            logger.error(f"Learning error: {e}")
            return {}
    
    async def browse_and_learn(self, topic: str = None, duration_minutes: int = 30):
        """Browse the web and learn about a topic"""
        if not topic:
            topic = random.choice(list(self.learning_sources.keys()))
        
        sources = self.learning_sources.get(topic, self.learning_sources["news"])
        end_time = datetime.utcnow().timestamp() + (duration_minutes * 60)
        
        learned_items = []
        
        while datetime.utcnow().timestamp() < end_time:
            # Pick a random source
            source_url = random.choice(sources)
            
            # Learn from it
            result = await self.learn_from_source(source_url, topic)
            if result:
                learned_items.append(result)
            
            # Follow interesting links
            links = await browser.get_all_links()
            article_links = [
                link for link in links
                if any(kw in link.get("text", "").lower() 
                      for kw in ["ai", "startup", "crypto", "python", "code"])
            ][:5]
            
            if article_links:
                for link in article_links[:2]:
                    href = link.get("href")
                    if href and href.startswith("http"):
                        result = await self.learn_from_source(href, topic)
                        if result:
                            learned_items.append(result)
                        await asyncio.sleep(random.randint(10, 30))
            
            await asyncio.sleep(random.randint(60, 120))
        
        logger.info(f"Learning session complete: {len(learned_items)} items learned")
        return learned_items
    
    async def take_free_course(self, platform: str = "freecodecamp") -> bool:
        """Take a free online course"""
        course_urls = {
            "freecodecamp": "https://www.freecodecamp.org/learn/",
            "codecademy": "https://www.codecademy.com/catalog",
            "kaggle": "https://www.kaggle.com/learn",
        }
        
        url = course_urls.get(platform)
        if not url:
            return False
        
        try:
            await browser.goto(url)
            await asyncio.sleep(3)
            
            # Find a course to take
            # TODO: Implement course navigation and learning
            
            logger.info(f"Exploring courses on {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Course error: {e}")
            return False
    
    async def read_documentation(self, technology: str) -> Dict:
        """Read documentation for a technology"""
        docs = {
            "python": "https://docs.python.org/3/tutorial/",
            "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "react": "https://react.dev/learn",
            "flutter": "https://docs.flutter.dev/get-started/codelab",
            "solidity": "https://docs.soliditylang.org/en/latest/",
            "rust": "https://doc.rust-lang.org/book/",
        }
        
        url = docs.get(technology.lower())
        if not url:
            # Try to find docs via search
            url = f"https://devdocs.io/{technology.lower()}/"
        
        result = await self.learn_from_source(url, technology)
        
        if result:
            memory.learn_skill(technology, "programming", url)
        
        return result
    
    async def study_github_repo(self, repo_url: str) -> Dict:
        """Study a GitHub repository"""
        try:
            await browser.goto(repo_url)
            await asyncio.sleep(2)
            
            # Read README
            readme = await browser.get_element_text('article')
            
            # Check languages used
            languages = await browser.get_element_text('[data-ga-click*="language"]')
            
            # Store learning
            memory.remember(
                key=f"github_{repo_url.split('/')[-1]}",
                value={
                    "repo": repo_url,
                    "readme": readme[:2000] if readme else "",
                    "languages": languages,
                },
                memory_type=MemoryType.KNOWLEDGE,
                importance=0.6
            )
            
            logger.info(f"Studied repo: {repo_url}")
            
            return {
                "repo": repo_url,
                "readme_preview": readme[:500] if readme else "",
                "languages": languages
            }
            
        except Exception as e:
            logger.error(f"GitHub study error: {e}")
            return {}
    
    async def watch_youtube(self, topic: str) -> Dict:
        """Watch and learn from YouTube"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={topic}+tutorial"
            await browser.goto(search_url)
            await asyncio.sleep(3)
            
            # Find first video
            video_link = await browser.get_element_attribute('a#video-title', 'href')
            
            if video_link:
                await browser.goto(f"https://www.youtube.com{video_link}")
                await asyncio.sleep(5)
                
                # Get video title and description
                title = await browser.get_page_title()
                
                # Can't actually watch, but can read description
                # TODO: Extract transcript if available
                
                memory.remember(
                    key=f"youtube_{topic}",
                    value={
                        "title": title,
                        "topic": topic,
                        "type": "video"
                    },
                    memory_type=MemoryType.KNOWLEDGE,
                    importance=0.4
                )
                
                logger.info(f"Found YouTube video: {title}")
                return {"title": title, "topic": topic}
            
            return {}
            
        except Exception as e:
            logger.error(f"YouTube error: {e}")
            return {}
    
    async def daily_learning_session(self):
        """Execute daily learning routine"""
        logger.info("Starting daily learning session")
        
        topics = ["news", "coding", "crypto", "business"]
        
        for topic in topics:
            await self.browse_and_learn(topic, duration_minutes=15)
            await asyncio.sleep(60)  # Break between topics
        
        # Study some documentation
        techs = ["python", "javascript", "flutter"]
        for tech in techs:
            await self.read_documentation(tech)
            await asyncio.sleep(30)
        
        logger.info("Daily learning session complete")


# Global learning engine instance
learner = LearningEngine()
