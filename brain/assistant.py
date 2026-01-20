import asyncio
from typing import Optional
from loguru import logger

from config.settings import config

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except:
    HAS_OPENAI = False


class AIAssistant:
    def __init__(self):
        self.client = None
        self.model = "gpt-4o"
        self.calls_today = 0
        self.max_calls = 100
        
    def init(self):
        if HAS_OPENAI and config.openai_api_key:
            self.client = AsyncOpenAI(api_key=config.openai_api_key)
            logger.info("OpenAI assistant ready (backup mode)")
        else:
            logger.info("OpenAI not configured - using free AI only")
    
    async def ask(self, question: str, context: str = "") -> str:
        if not self.client:
            return ""
        
        if self.calls_today >= self.max_calls:
            logger.warning("OpenAI daily limit reached")
            return ""
        
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Give concise, actionable answers."}
            ]
            if context:
                messages.append({"role": "user", "content": f"Context: {context}"})
            messages.append({"role": "user", "content": question})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            self.calls_today += 1
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return ""
    
    async def quick_answer(self, question: str) -> str:
        return await self.ask(question)
    
    async def solve_problem(self, problem: str) -> str:
        return await self.ask(f"How do I solve this: {problem}. Give step by step solution.")
    
    async def write_code(self, description: str) -> str:
        return await self.ask(f"Write Python code for: {description}. Include all imports. Code only, no explanation.")
    
    async def improve_text(self, text: str, purpose: str = "professional") -> str:
        return await self.ask(f"Improve this text for {purpose} use: {text}")
    
    async def summarize(self, text: str) -> str:
        return await self.ask(f"Summarize in 3 sentences: {text[:2000]}")
    
    def reset_daily(self):
        self.calls_today = 0


assistant = AIAssistant()
