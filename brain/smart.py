import asyncio
from typing import Optional
from loguru import logger

from config.settings import config

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except:
    HAS_OPENAI = False


class SmartAssistant:
    def __init__(self):
        self.client = None
        self.model = "gpt-4o-mini"
        self.calls_today = 0
        self.max_calls = 500
        
    def init(self):
        if HAS_OPENAI and config.openai_api_key:
            self.client = AsyncOpenAI(api_key=config.openai_api_key)
            logger.info("SmartAssistant ready (gpt-4o-mini)")
        else:
            logger.info("OpenAI not configured")
    
    async def ask(self, question: str, system: str = "You are a helpful assistant. Be concise.") -> str:
        if not self.client:
            return ""
        
        if self.calls_today >= self.max_calls:
            return ""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            self.calls_today += 1
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI error: {e}")
            return ""
    
    async def solve_leetcode(self, problem: str) -> str:
        system = "You are an expert programmer. Write clean, working Python code. Only output the code, no explanations."
        prompt = f"Solve this LeetCode problem:\n\n{problem}\n\nWrite the complete Solution class with all methods."
        return await self.ask(prompt, system)
    
    async def write_proposal(self, job: str, skills: str = "Python, Flutter, AI") -> str:
        system = "You are a professional freelancer writing job proposals. Be confident and specific."
        prompt = f"Write a short compelling proposal for this job:\n{job}\n\nMy skills: {skills}"
        return await self.ask(prompt, system)
    
    async def write_tweet(self, topic: str) -> str:
        system = "You are a tech influencer. Write engaging tweets. No hashtags."
        prompt = f"Write a tweet about: {topic}"
        result = await self.ask(prompt, system)
        return result[:280] if result else ""
    
    async def write_article(self, topic: str, words: int = 500) -> str:
        system = "You are a tech writer. Write informative articles."
        prompt = f"Write a {words} word article about: {topic}"
        return await self.ask(prompt, system)
    
    async def write_email(self, context: str, tone: str = "professional") -> str:
        system = f"You are writing {tone} emails. Be clear and concise."
        prompt = f"Write an email for this situation: {context}"
        return await self.ask(prompt, system)
    
    async def analyze_job(self, job: str) -> dict:
        system = "You analyze job postings. Return JSON only."
        prompt = f'''Analyze this job and return JSON:
{job}

Return: {{"relevant": true/false, "skills_match": 0-100, "hourly_rate": estimate, "apply": true/false}}'''
        result = await self.ask(prompt, system)
        try:
            import json
            return json.loads(result)
        except:
            return {"relevant": True, "apply": True}
    
    async def generate_ideas(self, area: str) -> list:
        system = "You generate business ideas. Be creative and practical."
        prompt = f"Give me 5 startup/side hustle ideas in: {area}. One line each."
        result = await self.ask(prompt, system)
        return result.split("\n") if result else []
    
    async def improve_text(self, text: str) -> str:
        system = "You improve text. Make it clearer and more impactful."
        prompt = f"Improve this text:\n{text}"
        return await self.ask(prompt, system)
    
    async def translate(self, text: str, to_lang: str = "English") -> str:
        system = f"You are a translator. Translate to {to_lang}."
        return await self.ask(text, system)
    
    def reset_daily(self):
        self.calls_today = 0


smart = SmartAssistant()
