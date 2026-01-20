import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
from loguru import logger

from brain.memory import memory, MemoryType
from brain.autonomous import brain


class ReasoningEngine:
    def __init__(self):
        self.context_stack = deque(maxlen=50)
        self.current_goal = None
        self.sub_goals = []
        self.problem_history = []
        
    def set_goal(self, goal: str):
        self.current_goal = goal
        self.sub_goals = self._decompose_goal(goal)
        
    def _decompose_goal(self, goal: str) -> List[str]:
        goal_lower = goal.lower()
        if "register" in goal_lower:
            return ["navigate to signup", "fill form", "submit", "verify", "complete profile"]
        elif "apply" in goal_lower:
            return ["find job", "read requirements", "prepare application", "submit", "follow up"]
        elif "post" in goal_lower:
            return ["create content", "find post area", "write", "publish", "verify"]
        elif "earn" in goal_lower or "money" in goal_lower:
            return ["find opportunities", "evaluate", "execute", "track progress"]
        else:
            return ["analyze", "plan", "execute", "verify"]
    
    def reason(self, observation: str, context: Dict = None) -> Dict:
        self.context_stack.append({"obs": observation, "time": datetime.utcnow().isoformat()})
        analysis = self._analyze(observation)
        action = self._decide_action(analysis)
        return {"analysis": analysis, "action": action, "confidence": self._get_confidence(analysis)}
    
    def _analyze(self, observation: str) -> Dict:
        obs_lower = observation.lower()
        return {
            "is_form": any(w in obs_lower for w in ["input", "form", "field", "enter"]),
            "is_error": any(w in obs_lower for w in ["error", "failed", "invalid", "wrong"]),
            "is_success": any(w in obs_lower for w in ["success", "welcome", "thank", "complete"]),
            "is_captcha": any(w in obs_lower for w in ["captcha", "verify", "robot"]),
            "is_otp": any(w in obs_lower for w in ["otp", "code", "verification"]),
            "is_login": any(w in obs_lower for w in ["login", "sign in", "password"]),
            "is_job": any(w in obs_lower for w in ["job", "apply", "position", "hiring"]),
        }
    
    def _decide_action(self, analysis: Dict) -> str:
        if analysis["is_error"]:
            return "handle_error"
        elif analysis["is_captcha"]:
            return "solve_captcha"
        elif analysis["is_otp"]:
            return "wait_and_enter_otp"
        elif analysis["is_login"]:
            return "fill_login"
        elif analysis["is_form"]:
            return "fill_form"
        elif analysis["is_success"]:
            return "proceed_to_next"
        elif analysis["is_job"]:
            return "evaluate_and_apply"
        else:
            return "explore"
    
    def _get_confidence(self, analysis: Dict) -> float:
        matches = sum(1 for v in analysis.values() if v)
        return min(1.0, matches * 0.25 + 0.5)
    
    def solve(self, problem: str) -> str:
        self.problem_history.append(problem)
        for old_problem, solution in memory.get_all_memories("knowledge"):
            if problem.lower()[:30] in str(old_problem).lower():
                return solution.get("action", "try previous approach")
        return brain.solve_problem(problem)
    
    def get_next_step(self) -> Optional[str]:
        if self.sub_goals:
            return self.sub_goals.pop(0)
        return None


class ContextManager:
    def __init__(self):
        self.current_page = ""
        self.current_platform = ""
        self.logged_in_platforms = set()
        self.active_tasks = []
        self.session_data = {}
        
    def update(self, url: str = "", page_text: str = ""):
        self.current_page = url
        self._detect_platform(url)
        
    def _detect_platform(self, url: str):
        platforms = {
            "twitter.com": "twitter", "x.com": "twitter",
            "linkedin.com": "linkedin",
            "medium.com": "medium",
            "upwork.com": "upwork",
            "fiverr.com": "fiverr",
            "github.com": "github",
            "facebook.com": "facebook",
            "instagram.com": "instagram",
        }
        for domain, platform in platforms.items():
            if domain in url:
                self.current_platform = platform
                return
        self.current_platform = "unknown"
    
    def mark_logged_in(self, platform: str):
        self.logged_in_platforms.add(platform)
        
    def is_logged_in(self, platform: str = None) -> bool:
        platform = platform or self.current_platform
        return platform in self.logged_in_platforms
    
    def add_task(self, task: str):
        self.active_tasks.append(task)
        
    def complete_task(self, task: str):
        if task in self.active_tasks:
            self.active_tasks.remove(task)
    
    def store(self, key: str, value: Any):
        self.session_data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        return self.session_data.get(key, default)


reasoning = ReasoningEngine()
context = ContextManager()
