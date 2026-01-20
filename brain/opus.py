import asyncio
import os
from loguru import logger
from config.settings import config

# Toggle for Opus API usage - set to "true" to enable
USE_OPUS = os.getenv("USE_OPUS", "false").lower() == "true"

try:
    from anthropic import AsyncAnthropic
    HAS_ANTHROPIC = True
except:
    HAS_ANTHROPIC = False

class OpusBrain:
    def __init__(self):
        self.client = None
        # Allow user to specify "claude-3-5-opus-20240229" or "claude-4.5-opus-thinking"
        # via ANTHROPIC_MODEL in jeph.env
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229") 
        
    def init(self):
        # Check if Opus is disabled via environment variable
        if not USE_OPUS:
            logger.info("OpusBrain disabled (USE_OPUS=false). Using OpenAI instead.")
            return
            
        key = config.ai.anthropic_api_key
        if HAS_ANTHROPIC and key:
            self.client = AsyncAnthropic(api_key=key)
            logger.info(f"OpusBrain ready ({self.model})")
        else:
            logger.warning("Anthropic API key missing or library not installed")

    async def think(self, prompt: str, system: str = "You are an expert AI.") -> str:
        if not self.client:
            return ""
            
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system=system,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Opus error: {e}")
            return ""

    async def architect_solution(self, requirements: str) -> str:
        system = "You are a Chief Software Architect. Design robust, scalable systems."
        prompt = f"""
        Design a full-stack solution for: {requirements}
        
        Output logic:
        1. File structure
        2. Technology stack choices (database, backend, frontend)
        3. Key API endpoints
        4. Deployment strategy (Docker)
        """
        return await self.think(prompt, system)

    async def write_code(self, file_path: str, context: str) -> str:
        system = "You are a Principal Engineer. Write clean, production-ready code."
        prompt = f"""
        Write the full content for file: {file_path}
        
        Context/Requirements:
        {context}
        
        Return ONLY the code, no markdown block syntax if possible, or inside a clean block.
        """
        return await self.think(prompt, system)
        
    async def improve_code(self, original_code: str) -> str:
        system = "You are a Code Optimization Expert. Improve performance, readability, and security."
        prompt = f"""
        Review and refactor this code to be better (faster, cleaner, stronger):
        
        {original_code}
        
        Return fully rewritten code.
        """
        return await self.think(prompt, system)

opus = OpusBrain()
