"""
Jephthah Medium Article Writer
Automated article publishing for thought leadership
"""

import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional

from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.vision import vision
from brain.memory import memory


class MediumWriter:
    """Medium automation for article publishing"""
    
    def __init__(self):
        self.base_url = "https://medium.com"
        self.logged_in = False
        
        # Article templates
        self.topics = [
            "AI and the Future of Work",
            "Building Startups in Your 20s",
            "Crypto Trading Lessons",
            "Flutter Development Tips",
            "Remote Work Productivity",
            "Tech Entrepreneurship",
            "Web3 and DeFi Insights",
            "Cold Email Strategies",
            "The Hustle Mindset",
            "Learning to Code Fast",
        ]
    
    async def login(self) -> bool:
        """Login to Medium"""
        if self.logged_in:
            return True
        
        username = config.social.medium_username
        password = config.social.medium_password
        
        if not username or not password:
            logger.warning("Medium credentials not configured")
            return False
        
        try:
            await browser.goto("https://medium.com/m/signin")
            await asyncio.sleep(2)
            
            # Click email sign in
            await browser.click_text("Sign in with email")
            await asyncio.sleep(1)
            
            # Enter email
            await browser.type_like_human('input[type="email"]', username)
            await browser.click_like_human('button[type="submit"]')
            await asyncio.sleep(2)
            
            # Enter password if shown
            password_field = await browser.wait_for_selector('input[type="password"]', timeout=5000)
            if password_field:
                await browser.type_like_human('input[type="password"]', password)
                await browser.click_like_human('button[type="submit"]')
                await asyncio.sleep(3)
            
            # Check if logged in
            if await vision.is_logged_in(["Write", "New story"]):
                self.logged_in = True
                logger.info("Medium login successful")
                return True
            else:
                logger.error("Medium login failed")
                return False
                
        except Exception as e:
            logger.error(f"Medium login error: {e}")
            return False
    
    async def write_article(self, title: str, content: str, tags: List[str] = None) -> bool:
        """Write and publish an article"""
        if not await self.login():
            return False
        
        try:
            # Go to new story
            await browser.goto("https://medium.com/new-story")
            await asyncio.sleep(3)
            
            # Enter title
            title_selector = '[data-contents="true"] h3, [placeholder="Title"]'
            await browser.click_like_human(title_selector)
            await browser.type_like_human(title_selector, title)
            await asyncio.sleep(1)
            
            # Enter content
            content_selector = '[data-contents="true"] p, [placeholder="Tell your story…"]'
            await browser.click_like_human(content_selector)
            
            # Type content with paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                await browser.type_like_human(content_selector, para)
                await browser.page.keyboard.press('Enter')
                await browser.page.keyboard.press('Enter')
                await asyncio.sleep(0.5)
            
            await asyncio.sleep(2)
            
            # Publish
            await browser.click_like_human('button:has-text("Publish")')
            await asyncio.sleep(2)
            
            # Add tags if provided
            if tags:
                for tag in tags[:5]:  # Medium allows max 5 tags
                    tag_input = '[placeholder="Add a tag"]'
                    await browser.type_like_human(tag_input, tag)
                    await browser.page.keyboard.press('Enter')
                    await asyncio.sleep(0.5)
            
            # Final publish
            await browser.click_like_human('button:has-text("Publish now")')
            await asyncio.sleep(3)
            
            logger.info(f"Article published: {title}")
            
            memory.log_action(
                action_type="content/article",
                description=f"Published Medium article",
                target="medium",
                result="success",
                details={"title": title, "tags": tags}
            )
            
            # Update goals
            # TODO: Increment article count goal
            
            return True
            
        except Exception as e:
            logger.error(f"Article publish error: {e}")
            return False
    
    def generate_article(self, topic: str = None) -> Dict:
        """Generate article content based on topic"""
        if not topic:
            topic = random.choice(self.topics)
        
        # Article templates based on topic
        templates = {
            "AI and the Future of Work": {
                "title": "How AI is Reshaping the Way We Work (And Why You Should Care)",
                "content": """
The workspace of 2025 looks nothing like what we imagined a decade ago.

AI isn't just automating tasks—it's fundamentally changing what it means to be productive. As someone who builds AI systems daily, I've seen firsthand how this technology transforms workflows.

Here's what most people get wrong about AI and work:

**1. AI Won't Replace You—But Someone Using AI Will**

The fear of job replacement is overblown. What's real is the productivity gap between those who leverage AI and those who don't. I've seen developers ship code 10x faster using AI assistants.

**2. The New Skills That Matter**

- Prompt engineering
- AI-assisted learning
- Human-AI collaboration
- Critical thinking (more important than ever)

**3. How I Use AI Daily**

Every morning, I use AI to:
- Summarize emails
- Draft responses
- Research topics
- Generate code scaffolds
- Create content outlines

This frees me to focus on strategy and creativity—the truly human elements.

**The Bottom Line**

Embrace AI as a tool, not a threat. The future belongs to those who learn to work alongside intelligent systems.

What's your experience with AI at work? Let me know in the comments.

---
*Jephthah Ameh is a tech entrepreneur and AI developer. Follow for more insights on tech and business.*
""",
                "tags": ["AI", "Future of Work", "Technology", "Productivity", "Career"]
            },
            # Add more templates...
        }
        
        if topic in templates:
            return templates[topic]
        else:
            # Generic template
            return {
                "title": f"What I Learned About {topic} This Week",
                "content": f"""
This week, I dove deep into {topic}. Here's what I discovered.

**The Key Insight**

{topic} is more important than most people realize. In today's rapidly changing world, understanding this topic can make or break your success.

**Three Things I Learned**

1. Start small, but start now
2. Consistency beats intensity
3. Learn from those who've done it before

**My Action Plan**

I'm committing to spending more time mastering {topic}. Will you join me?

---
*Follow me for daily insights on tech, business, and personal growth.*
""",
                "tags": [topic.split()[0], "Tech", "Learning", "Growth", "Insights"]
            }
    
    async def daily_article(self):
        """Publish daily article"""
        topic = random.choice(self.topics)
        article = self.generate_article(topic)
        
        success = await self.write_article(
            title=article["title"],
            content=article["content"],
            tags=article.get("tags", [])
        )
        
        if success:
            memory.learn_skill("Article Writing", "content", "Medium")
        
        return success


# Global Medium writer instance
medium = MediumWriter()
