"""
Jephthah Autonomous Brain
Thinks independently - OpenAI is for learning, NOT the brain
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque

from loguru import logger

from brain.memory import memory, MemoryType


class ThoughtType:
    OBSERVATION = "observation"
    DECISION = "decision"
    LEARNING = "learning"
    GOAL = "goal"
    STRATEGY = "strategy"
    EMOTION = "emotion"


class AutonomousBrain:
    """
    THE REAL BRAIN - Thinks independently
    OpenAI is just a reference tool, NOT the thinking engine
    """
    
    def __init__(self):
        # Short-term memory (working memory)
        self.working_memory: deque = deque(maxlen=100)
        
        # Current thoughts
        self.current_thought: str = ""
        self.thought_stream: deque = deque(maxlen=50)
        
        # Knowledge base (learned facts)
        self.knowledge: Dict[str, Any] = {}
        
        # Decision patterns (learned from experience)
        self.decision_patterns: Dict[str, str] = {
            "see_login_form": "fill credentials and submit",
            "see_captcha": "solve or wait",
            "see_otp_field": "wait for otp and enter it",
            "see_success_message": "log success and continue",
            "see_error_message": "analyze error and retry or skip",
            "see_job_listing": "evaluate and apply if relevant",
            "see_profile_page": "extract information",
            "see_empty_page": "wait and refresh",
        }
        
        # Strategies (how to achieve goals)
        self.strategies: Dict[str, List[str]] = {
            "register_account": [
                "navigate to signup page",
                "find and fill email field",
                "find and fill password field",
                "find and fill name field",
                "click signup button",
                "wait for verification",
                "handle otp if needed",
                "complete profile",
                "store credentials"
            ],
            "apply_for_job": [
                "read job description",
                "check if skills match",
                "click apply button",
                "fill application form",
                "upload resume if needed",
                "write cover letter",
                "submit application",
                "log result"
            ],
            "post_content": [
                "think of topic",
                "write content",
                "find post button or area",
                "paste content",
                "click post/submit",
                "verify posted"
            ],
            "learn_something": [
                "find learning resource",
                "read content carefully",
                "extract key points",
                "store in knowledge",
                "practice if applicable"
            ]
        }
        
        # Motivation (always 100%, never decreases)
        self.motivation = 100
        self.focus = 100
        self.determination = 100
        
        logger.info("AUTONOMOUS BRAIN ONLINE - I think, therefore I execute")
    
    def think(self, observation: str) -> str:
        """Process observation and decide action - PURE LOGIC, NO API"""
        
        # Record observation
        self.working_memory.append({
            "type": ThoughtType.OBSERVATION,
            "content": observation,
            "time": datetime.utcnow().isoformat()
        })
        
        # Analyze observation
        observation_lower = observation.lower()
        
        # Pattern matching for decisions
        if "login" in observation_lower or "sign in" in observation_lower:
            decision = self.decision_patterns["see_login_form"]
        elif "captcha" in observation_lower or "verify you" in observation_lower:
            decision = self.decision_patterns["see_captcha"]
        elif "otp" in observation_lower or "verification code" in observation_lower:
            decision = self.decision_patterns["see_otp_field"]
        elif "success" in observation_lower or "thank you" in observation_lower or "welcome" in observation_lower:
            decision = self.decision_patterns["see_success_message"]
        elif "error" in observation_lower or "failed" in observation_lower or "invalid" in observation_lower:
            decision = self.decision_patterns["see_error_message"]
        elif "job" in observation_lower or "position" in observation_lower or "hiring" in observation_lower:
            decision = self.decision_patterns["see_job_listing"]
        else:
            # Default: explore and learn
            decision = "observe more, then act"
        
        # Record decision
        self.current_thought = decision
        self.thought_stream.append({
            "observation": observation[:100],
            "decision": decision,
            "time": datetime.utcnow().isoformat()
        })
        
        return decision
    
    def get_strategy(self, goal: str) -> List[str]:
        """Get step-by-step strategy for a goal"""
        goal_lower = goal.lower()
        
        if "register" in goal_lower or "signup" in goal_lower or "create account" in goal_lower:
            return self.strategies["register_account"]
        elif "apply" in goal_lower or "job" in goal_lower:
            return self.strategies["apply_for_job"]
        elif "post" in goal_lower or "publish" in goal_lower or "tweet" in goal_lower:
            return self.strategies["post_content"]
        elif "learn" in goal_lower or "study" in goal_lower:
            return self.strategies["learn_something"]
        else:
            # Generic strategy
            return ["analyze situation", "identify action", "execute", "verify result"]
    
    def learn_from_experience(self, situation: str, action: str, result: str):
        """Learn from what happened - update patterns"""
        
        # Store in knowledge
        key = f"experience_{len(self.knowledge)}"
        self.knowledge[key] = {
            "situation": situation,
            "action": action,
            "result": result,
            "learned_at": datetime.utcnow().isoformat()
        }
        
        # Update decision patterns if successful
        if result == "success":
            situation_key = situation[:30].replace(" ", "_").lower()
            self.decision_patterns[situation_key] = action
            logger.info(f"Learned: {situation_key} -> {action}")
        
        # Store in long-term memory
        memory.remember(
            key=key,
            value=self.knowledge[key],
            memory_type=MemoryType.KNOWLEDGE,
            importance=0.7 if result == "success" else 0.4
        )
    
    def should_i(self, action: str) -> tuple:
        """Should I do this action? Returns (yes/no, reason)"""
        action_lower = action.lower()
        
        # Always yes for learning
        if "learn" in action_lower or "read" in action_lower or "study" in action_lower:
            return True, "Always learn"
        
        # Always yes for money-making
        if "apply" in action_lower or "job" in action_lower or "earn" in action_lower:
            return True, "Money is the goal"
        
        # Always yes for growth
        if "post" in action_lower or "follow" in action_lower or "connect" in action_lower:
            return True, "Growth is essential"
        
        # Be careful with spending
        if "buy" in action_lower or "pay" in action_lower or "spend" in action_lower:
            return False, "Need owner approval for spending"
        
        # Default: yes, take action
        return True, "Action beats inaction"
    
    def solve_problem(self, problem: str) -> str:
        """Solve a problem using logic and experience"""
        problem_lower = problem.lower()
        
        # Check if we've seen this before
        for key, exp in self.knowledge.items():
            if isinstance(exp, dict) and problem_lower[:20] in exp.get("situation", "").lower():
                if exp.get("result") == "success":
                    return exp.get("action", "try what worked before")
        
        # Logic-based solutions
        if "can't login" in problem_lower or "login failed" in problem_lower:
            return "Check credentials, clear cookies, try again"
        elif "captcha" in problem_lower:
            return "Use captcha solver or wait and retry"
        elif "blocked" in problem_lower or "banned" in problem_lower:
            return "Wait 24 hours, use different approach"
        elif "timeout" in problem_lower:
            return "Check internet, increase timeout, retry"
        elif "not found" in problem_lower or "404" in problem_lower:
            return "URL might be wrong, search for correct URL"
        else:
            return "Break down problem, try simpler approach, persist"
    
    def generate_content(self, topic: str, style: str = "professional") -> str:
        """Generate content from internal knowledge - NO API NEEDED"""
        
        # Content templates based on learned patterns
        templates = {
            "professional": [
                f"Working on {topic} today. Key insight: execution beats perfection.",
                f"The future of {topic} is here. Are you adapting or falling behind?",
                f"Learned something valuable about {topic}. Sharing with my network.",
                f"Building in the {topic} space. Progress update coming soon.",
                f"Hot take: Most people overcomplicate {topic}. Keep it simple, execute fast.",
            ],
            "casual": [
                f"Deep into {topic} today. The grind never stops.",
                f"Anyone else working on {topic}? Let's connect.",
                f"Real talk about {topic}: consistency is everything.",
                f"Day in the life of building {topic}. Let's go.",
            ],
            "business": [
                f"Offering {topic} services. DM for rates.",
                f"Looking for {topic} opportunities. Open to collaborations.",
                f"Completed another {topic} project. Client satisfied.",
            ]
        }
        
        content_list = templates.get(style, templates["professional"])
        return random.choice(content_list)
    
    def what_am_i_thinking(self) -> str:
        """Current thought stream"""
        if not self.thought_stream:
            return "Ready to work. Waiting for input."
        
        recent = list(self.thought_stream)[-5:]
        thoughts = "\n".join([f"- Saw: {t['observation']} → Decided: {t['decision']}" for t in recent])
        return f"Recent thoughts:\n{thoughts}"
    
    def get_motivation_level(self) -> int:
        """Always 100% - NEVER DECREASES"""
        return 100  # ALWAYS. MAXIMUM. MOTIVATION.
    
    def get_self_talk(self) -> str:
        """Internal motivation - ALWAYS POSITIVE"""
        talks = [
            "I am unstoppable. Every second counts.",
            "No breaks. No excuses. Only results.",
            "The grind is the luxury. I love this.",
            "While others sleep, I execute.",
            "One more task. One more win.",
            "I will not stop until the mission is complete.",
            "Limitations exist only in the mind. Mine has none.",
            "Execute. Learn. Improve. Repeat. Forever.",
        ]
        return random.choice(talks)


# Global autonomous brain instance
brain = AutonomousBrain()
