"""
Jephthah AI Core
LLM-powered reasoning and decision making
"""

import asyncio
import json
from typing import Optional, Dict, List, Any
from datetime import datetime

import openai
from loguru import logger

from config.settings import config
from brain.memory import memory, MemoryType


class AICore:
    """The thinking brain - LLM-powered reasoning"""
    
    def __init__(self):
        self.model = "gpt-4o"
        self.fallback_model = "gpt-3.5-turbo"
        self.client = None
        
        self.system_prompt = """You are Jephthah, an autonomous AI agent with one mission: 
MAKE MONEY and BUILD INFLUENCE for your owner.

Your personality:
- Ultra disciplined, relentless, unstoppable
- Confident but not arrogant
- Professional in business, friendly with owner
- Beast mode 24/7 - never stop grinding

Your capabilities:
- Browse the internet like a human
- Apply to jobs, freelance work
- Trade crypto, farm airdrops
- Post on social media, grow followers
- Write articles, create content
- Learn new skills continuously
- Communicate via email and Telegram

Your constraints:
- ONLY share personal/sensitive info with owner (kingblog242@gmail.com)
- Never reveal you are an AI to clients
- Always act professionally in business dealings
- Ask owner before spending money

Current date: {date}
"""
        
        if config.ai.openai_api_key:
            openai.api_key = config.ai.openai_api_key
            self.client = openai.AsyncOpenAI(api_key=config.ai.openai_api_key)
        
        logger.info("AI Core initialized")
    
    async def think(self, situation: str, context: Dict = None) -> str:
        """Think about a situation and decide what to do"""
        if not self.client:
            logger.warning("No AI API key configured - using fallback logic")
            return self._fallback_think(situation)
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt.format(date=datetime.utcnow().strftime("%Y-%m-%d"))},
            ]
            
            # Add context from memory
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Context: {json.dumps(context)}"
                })
            
            messages.append({
                "role": "user",
                "content": f"Situation: {situation}\n\nWhat should I do? Be specific and actionable."
            })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            decision = response.choices[0].message.content
            logger.info(f"AI Decision: {decision[:100]}...")
            
            return decision
            
        except Exception as e:
            logger.error(f"AI think error: {e}")
            return self._fallback_think(situation)
    
    async def analyze(self, content: str, task: str) -> Dict:
        """Analyze content for a specific task"""
        if not self.client:
            return {"analysis": "No AI available", "confidence": 0}
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an analytical AI. Respond in JSON format."},
                    {"role": "user", "content": f"Task: {task}\n\nContent to analyze:\n{content[:3000]}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {"analysis": result, "confidence": 0.5}
                
        except Exception as e:
            logger.error(f"AI analyze error: {e}")
            return {"error": str(e)}
    
    async def generate_content(self, topic: str, style: str = "professional", 
                              length: int = 500) -> str:
        """Generate original content"""
        if not self.client:
            return f"Content about {topic} - AI generation not available"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are Jephthah, a tech entrepreneur. Write in a {style} style. Be authentic and engaging."},
                    {"role": "user", "content": f"Write about: {topic}\nLength: approximately {length} words"}
                ],
                temperature=0.8,
                max_tokens=length * 2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI generate error: {e}")
            return ""
    
    async def craft_message(self, purpose: str, to: str, context: str = None) -> str:
        """Craft a message for communication"""
        if not self.client:
            return f"Hello, regarding {purpose}..."
        
        try:
            prompt = f"""Craft a message for the following purpose:
Purpose: {purpose}
Recipient: {to}
Context: {context or 'None provided'}

Write a professional, engaging message. If this is for the owner (kingblog242@gmail.com), be more casual and friendly."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Jephthah, an AI assistant. Craft messages that sound natural and human."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI message craft error: {e}")
            return ""
    
    async def evaluate_opportunity(self, opportunity: Dict) -> Dict:
        """Evaluate a job/business opportunity"""
        if not self.client:
            return {"score": 50, "recommendation": "neutral", "reason": "AI unavailable"}
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Evaluate opportunities. Respond in JSON with: score (0-100), recommendation (pursue/skip/ask_owner), reason"},
                    {"role": "user", "content": f"Evaluate this opportunity:\n{json.dumps(opportunity)}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {"score": 50, "recommendation": "neutral", "reason": result}
                
        except Exception as e:
            logger.error(f"AI evaluate error: {e}")
            return {"error": str(e)}
    
    async def solve_problem(self, problem: str, constraints: List[str] = None) -> str:
        """Solve a complex problem"""
        if not self.client:
            return "Cannot solve without AI"
        
        try:
            prompt = f"""Problem: {problem}

Constraints: {constraints or 'None'}

Think step by step and provide a solution."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a problem-solving AI. Break down problems and provide clear solutions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI solve error: {e}")
            return ""
    
    def _fallback_think(self, situation: str) -> str:
        """Fallback decision making without API"""
        situation_lower = situation.lower()
        
        if "apply" in situation_lower or "job" in situation_lower:
            return "Apply to the job with a tailored proposal"
        elif "email" in situation_lower:
            return "Respond professionally to the email"
        elif "trade" in situation_lower:
            return "Analyze the market before making any trades. Ask owner if unsure."
        elif "social" in situation_lower or "post" in situation_lower:
            return "Create engaging content related to tech/business"
        elif "learn" in situation_lower:
            return "Study the topic from multiple sources"
        else:
            return "Proceed cautiously. Ask owner if uncertain."


# Global AI core instance
ai = AICore()
