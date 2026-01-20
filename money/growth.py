import asyncio
import random
from typing import List, Dict
from loguru import logger
from brain.smart import smart
from config.settings import config

class GrowthHacker:
    def __init__(self):
        self.portfolio_url = config.identity.website or "https://jephthahameh.cfd"
        self.templates = {
            "cold_pitch": [
                f"Hi {{name}},\n\nI noticed {{problem}} on your site. I can fix it by {{solution}}. You can check my work here: {self.portfolio_url}\n\nOpen to a quick chat?",
                f"Hey {{name}},\n\nI'm a developer who specializes in {{niche}}. I built {{portfolio_item}}. See more at {self.portfolio_url}. Would love to help you scale.",
                f"Hello {{name}},\n\nSaw you're hiring for {{role}}. I don't just fit the description, I automate the entire workflow. Portfolio: {self.portfolio_url}"
            ],
            "follow_up": [
                "Hi {name}, just bumping this.",
                "Hey {name}, any thoughts on my previous email?"
            ]
        }
        self.ab_tests = {}  # Store results: {"template_id": {"sent": 0, "replied": 0}}

    async def generate_cold_email(self, prospect: Dict) -> str:
        # Select best performing template or random for exploration
        template = random.choice(self.templates["cold_pitch"])
        
        # Use AI to customize
        customized = await smart.ask(f"Customize this email for {prospect.get('name')} who runs {prospect.get('company')}. Keep it short and punchy.\n\nTemplate: {template}")
        return customized

    async def track_response(self, template_id: str, responded: bool):
        if template_id not in self.ab_tests:
            self.ab_tests[template_id] = {"sent": 0, "replied": 0}
        
        self.ab_tests[template_id]["sent"] += 1
        if responded:
            self.ab_tests[template_id]["replied"] += 1

class PortfolioManager:
    def __init__(self):
        self.url = config.identity.website or "https://jephthahameh.cfd"
    
    async def get_portfolio_link(self) -> str:
        return self.url

    async def add_project_to_portfolio(self, project: Dict):
        # In a real scenario, this would POST to a CMS or update a DB
        # For now, we assume the portfolio is static or managed elsewhere
        logger.info(f"Project {project['title']} ready to be added to {self.url}")

growth = GrowthHacker()
portfolio = PortfolioManager()
