import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from brain.memory import memory


class ContentCreator:
    def __init__(self):
        self.topics = [
            "AI automation", "remote work", "crypto trading", "startup life",
            "freelancing tips", "tech career", "web3", "productivity hacks",
            "coding tutorials", "side hustles", "building in public"
        ]
        self.hooks = [
            "Most people don't know this about {topic}...",
            "I made ${amount} with {topic}. Here's how:",
            "Stop doing {topic} wrong. Here's the truth:",
            "The future of {topic} is here. Are you ready?",
            "{topic} changed my life. Let me explain:",
            "Hot take: {topic} is overrated. Here's why:",
            "I spent 1000 hours learning {topic}. Key lessons:",
        ]
        
    def generate_tweet(self, topic: str = None) -> str:
        topic = topic or random.choice(self.topics)
        hook = random.choice(self.hooks).format(
            topic=topic,
            amount=random.choice(["10K", "50K", "100K"])
        )
        return hook
    
    def generate_thread(self, topic: str = None, length: int = 5) -> List[str]:
        topic = topic or random.choice(self.topics)
        thread = [f"🧵 THREAD: Everything you need to know about {topic}:\n\n(Save this)"]
        points = [
            "1/ First, understand the fundamentals.",
            "2/ Most people skip this step. Don't.",
            "3/ The secret is consistency over perfection.",
            "4/ Real talk: it takes time. But it's worth it.",
            "5/ Action beats theory every single time."
        ]
        thread.extend(points[:length-1])
        thread.append(f"\nIf this helped, follow @jephthahameh for more on {topic}.\n\nLike + RT the first tweet 🙏")
        return thread
    
    def generate_article(self, topic: str = None) -> Dict:
        topic = topic or random.choice(self.topics)
        title = f"The Complete Guide to {topic.title()} in 2025"
        content = f"""# {title}

If you want to succeed with {topic}, you need to understand a few things first.

## Why {topic.title()} Matters

In today's world, {topic} isn't optional anymore. It's essential.

Here's what I've learned after years of experience:

### 1. Start Before You're Ready

Waiting for the "right time" is a trap. There's never a perfect moment.

### 2. Invest in Learning

The best return on investment is always education. Read, practice, repeat.

### 3. Build in Public

Share your journey. People connect with authenticity.

### 4. Stay Consistent

One day of work means nothing. One year of consistent effort means everything.

## The Bottom Line

{topic.title()} is an opportunity. But only for those who take action.

---

*Follow me for more insights on tech, business, and building the life you want.*
"""
        return {"title": title, "content": content, "topic": topic}
    
    def generate_linkedin_post(self, topic: str = None) -> str:
        topic = topic or random.choice(self.topics)
        return f"""I've been thinking a lot about {topic} lately.

Here's what I realized:

Success isn't about having all the answers.
It's about taking action despite uncertainty.

{topic.title()} taught me this.

What's your experience with {topic}? Let's discuss in the comments.

#TechCareer #BuildInPublic #Entrepreneurship"""

    def generate_email_response(self, context: str = "job inquiry") -> str:
        templates = {
            "job inquiry": """Thank you for reaching out!

I'd be happy to discuss this opportunity further. My experience includes:
- 5+ years in software development
- Expertise in Python, Flutter, React
- Strong background in AI/automation

I'm available for a call at your earliest convenience.

Best regards,
Jephthah Ameh""",
            "freelance": """Hi,

Thank you for your interest in my services.

I specialize in:
- Custom software development
- AI/automation solutions
- Mobile app development

I'd love to learn more about your project. What's your timeline?

Best,
Jephthah""",
        }
        return templates.get(context, templates["freelance"])


class ResumeGenerator:
    def __init__(self):
        self.skills = {
            "languages": ["Python", "JavaScript", "Dart", "TypeScript", "Solidity"],
            "frameworks": ["Flutter", "React", "Node.js", "FastAPI", "Django"],
            "tools": ["Git", "Docker", "AWS", "Firebase", "PostgreSQL"],
            "areas": ["AI/ML", "Automation", "Web3", "Mobile Development", "API Design"]
        }
        
    def generate(self, job_type: str = "developer") -> str:
        return f"""JEPHTHAH AMEH
Software Developer | AI Specialist | Entrepreneur

📧 hireme@jephthahameh.cfd
🌐 jephthahameh.cfd
📍 Remote

---

SUMMARY
Passionate developer with expertise in AI, automation, and full-stack development.
Built and shipped 50+ projects. Always learning, always building.

---

SKILLS
Languages: {', '.join(self.skills['languages'])}
Frameworks: {', '.join(self.skills['frameworks'])}
Tools: {', '.join(self.skills['tools'])}
Areas: {', '.join(self.skills['areas'])}

---

EXPERIENCE
Freelance Developer | 2020 - Present
- Delivered 100+ projects for clients worldwide
- Specialized in automation and AI solutions
- 5-star rating on major freelancing platforms

Tech Entrepreneur | 2018 - Present
- Founded multiple tech startups
- Built products used by 10,000+ users

---

EDUCATION
Self-taught + Online Courses
Computer Science fundamentals, AI/ML, Web Development

---

Available for remote work immediately.
"""
    
    def generate_cover_letter(self, company: str = "Company", role: str = "Developer") -> str:
        return f"""Dear Hiring Manager,

I'm excited to apply for the {role} position at {company}.

With my background in software development and passion for building impactful products, I believe I can contribute significantly to your team.

Key highlights:
- 5+ years of professional development experience
- Track record of delivering projects on time
- Strong problem-solving and communication skills

I'd welcome the opportunity to discuss how I can add value to {company}.

Best regards,
Jephthah Ameh
hireme@jephthahameh.cfd"""


content_creator = ContentCreator()
resume_gen = ResumeGenerator()
