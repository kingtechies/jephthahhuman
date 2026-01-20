"""
Jephthah Creativity Engine
Original idea generation and innovation
"""

import random
from typing import List, Dict, Optional
from datetime import datetime

from loguru import logger

from brain.memory import memory, MemoryType
from brain.ai_core import ai


class CreativityEngine:
    """Generate original ideas and creative solutions"""
    
    def __init__(self):
        # Idea bank
        self.ideas: List[Dict] = []
        self.implemented_ideas: List[str] = []
        
        # Creative patterns
        self.startup_patterns = [
            "Uber for {industry}",
            "AI-powered {product}",
            "Web3 {service}",
            "{existing_product} but for {niche}",
            "Automated {task}",
            "SaaS for {profession}",
        ]
        
        self.content_patterns = [
            "How I made ${amount} with {method}",
            "Why {popular_belief} is wrong",
            "{number} things I learned from {experience}",
            "The future of {technology}",
            "From {start} to {end}: My journey",
            "Stop doing {common_mistake}",
        ]
        
        self.industries = [
            "real estate", "healthcare", "education", "finance",
            "legal", "fitness", "food", "travel", "e-commerce",
            "gaming", "entertainment", "construction"
        ]
        
        self.niches = [
            "developers", "freelancers", "small businesses",
            "content creators", "crypto traders", "remote workers",
            "students", "entrepreneurs", "agencies"
        ]
        
        logger.info("Creativity engine initialized")
    
    async def generate_startup_idea(self) -> Dict:
        """Generate a startup idea"""
        pattern = random.choice(self.startup_patterns)
        industry = random.choice(self.industries)
        niche = random.choice(self.niches)
        
        # Generate with AI if available
        concept = pattern.format(
            industry=industry,
            product="tool",
            service="marketplace",
            existing_product="Notion",
            niche=niche,
            task="lead generation",
            profession="developers"
        )
        
        idea = {
            "type": "startup",
            "concept": concept,
            "industry": industry,
            "target": niche,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "new"
        }
        
        # Get AI elaboration
        if ai.client:
            elaboration = await ai.generate_content(
                f"Elaborate on this startup idea: {concept}. Include problem, solution, revenue model.",
                style="professional",
                length=200
            )
            idea["elaboration"] = elaboration
        
        self.ideas.append(idea)
        logger.info(f"Generated startup idea: {concept}")
        
        return idea
    
    async def generate_content_idea(self, platform: str = "twitter") -> Dict:
        """Generate a content idea for social media"""
        pattern = random.choice(self.content_patterns)
        
        # Fill in the pattern
        content = pattern.format(
            amount=random.choice(["10K", "50K", "100K"]),
            method=random.choice(["freelancing", "trading", "building apps"]),
            popular_belief=random.choice(["college is necessary", "you need experience", "luck matters"]),
            number=random.choice(["5", "7", "10"]),
            experience=random.choice(["building startups", "failing", "getting rejected"]),
            technology=random.choice(["AI", "Web3", "remote work"]),
            start=random.choice(["$0", "failure", "nothing"]),
            end=random.choice(["$1M", "success", "everything"]),
            common_mistake=random.choice(["perfecting resumes", "waiting for opportunities", "asking for permission"])
        )
        
        idea = {
            "type": "content",
            "platform": platform,
            "hook": content,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Get full content from AI
        if ai.client and platform in ["medium", "blog"]:
            full_content = await ai.generate_content(
                f"Write an engaging article with this hook: {content}",
                style="conversational",
                length=500
            )
            idea["full_content"] = full_content
        elif ai.client:
            tweet = await ai.generate_content(
                f"Write a viral tweet thread (5 tweets) starting with: {content}",
                style="twitter",
                length=200
            )
            idea["thread"] = tweet
        
        self.ideas.append(idea)
        return idea
    
    async def brainstorm(self, topic: str, count: int = 5) -> List[str]:
        """Brainstorm ideas on a topic"""
        if ai.client:
            response = await ai.generate_content(
                f"Brainstorm {count} innovative ideas about: {topic}",
                style="creative",
                length=300
            )
            ideas = response.split("\n")
            return [idea.strip() for idea in ideas if idea.strip()]
        else:
            return [f"Idea about {topic} #{i}" for i in range(count)]
    
    async def solve_creatively(self, problem: str) -> str:
        """Creative problem solving"""
        if ai.client:
            return await ai.solve_problem(
                problem,
                constraints=["be creative", "think outside the box", "consider unconventional approaches"]
            )
        else:
            return f"Creative solution needed for: {problem}"
    
    def combine_ideas(self, idea1: str, idea2: str) -> str:
        """Combine two ideas into something new"""
        combinations = [
            f"What if we combined {idea1} with {idea2}?",
            f"{idea1} powered by {idea2}",
            f"A {idea1} that also does {idea2}",
        ]
        return random.choice(combinations)
    
    async def generate_gig_idea(self) -> Dict:
        """Generate a freelance gig/service idea"""
        services = [
            "AI chatbot development",
            "Web scraping automation",
            "Mobile app MVP",
            "Landing page design",
            "API integration",
            "Trading bot development",
            "Discord/Telegram bot",
            "SEO optimization",
            "Social media automation",
            "Data analysis dashboard"
        ]
        
        service = random.choice(services)
        
        idea = {
            "type": "gig",
            "service": service,
            "price_range": f"${random.randint(100, 500)} - ${random.randint(500, 2000)}",
            "platforms": ["Upwork", "Fiverr", "Freelancer"],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if ai.client:
            description = await ai.generate_content(
                f"Write a compelling gig description for: {service}",
                style="professional",
                length=150
            )
            idea["description"] = description
        
        return idea
    
    def get_random_motivation(self) -> str:
        """Get a creative motivational message"""
        messages = [
            "Every empire started with a single decision. Make yours today.",
            "While others sleep, I build. That's the difference.",
            "Your competition is watching Netflix. You're building the future.",
            "Broke is temporary. Giving up is permanent.",
            "The code you write today pays you tomorrow.",
            "Ship fast, iterate faster, fail fastest.",
            "Your 20s are for building. Build like your life depends on it.",
            "One focused hour beats eight distracted ones.",
            "The internet is the great equalizer. Use it.",
            "Make something people want. Make money doing it."
        ]
        return random.choice(messages)
    
    def daily_ideas(self) -> List[Dict]:
        """Generate daily ideas batch"""
        return self.ideas[-10:]  # Return last 10 ideas


# Global creativity instance
creativity = CreativityEngine()
