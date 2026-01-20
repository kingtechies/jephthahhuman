"""
Jephthah Goal Management System
Hierarchical goals with progress tracking
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum
from loguru import logger

from brain.memory import memory, Goal


class GoalCategory(str, Enum):
    INCOME = "income"
    SOCIAL = "social"
    LEARNING = "learning"
    NETWORKING = "networking"
    CONTENT = "content"
    TRADING = "trading"
    FREELANCE = "freelance"


class GoalManager:
    """Manages Jephthah's goals and objectives"""
    
    def __init__(self):
        self._init_master_goals()
        logger.info("Goal manager initialized")
    
    def _init_master_goals(self):
        """Initialize the primary goals if not exists"""
        existing = memory.get_active_goals()
        if not existing:
            # Master income goal
            master = memory.set_goal(
                title="Earn $1,000,000 in 2026",
                description="Generate one million dollars through freelancing, trading, and content",
                category=GoalCategory.INCOME.value,
                target_value=1000000,
                unit="USD",
                deadline=datetime(2026, 12, 31),
                priority=10
            )
            
            # Break down into monthly goals
            monthly_target = 1000000 / 12  # ~$83,333/month
            for month in range(1, 13):
                memory.set_goal(
                    title=f"Earn ${monthly_target:.0f} in Month {month}",
                    description=f"Monthly income target for month {month}",
                    category=GoalCategory.INCOME.value,
                    target_value=monthly_target,
                    unit="USD",
                    deadline=datetime(2026, month, 28),
                    priority=9,
                    parent_goal_id=master.id
                )
            
            # Social media goals
            memory.set_goal(
                title="Reach 1,000,000 Twitter followers",
                description="Build massive Twitter presence over 2 years",
                category=GoalCategory.SOCIAL.value,
                target_value=1000000,
                unit="followers",
                deadline=datetime(2028, 1, 1),
                priority=8
            )
            
            # Learning goals
            memory.set_goal(
                title="Master 10 programming languages",
                description="Become proficient in Python, JavaScript, Rust, Go, Solidity, etc.",
                category=GoalCategory.LEARNING.value,
                target_value=10,
                unit="languages",
                deadline=datetime(2026, 12, 31),
                priority=7
            )
            
            # Freelancing goals
            memory.set_goal(
                title="Get 40+ active clients",
                description="Maintain relationships with 40+ paying clients",
                category=GoalCategory.FREELANCE.value,
                target_value=40,
                unit="clients",
                deadline=datetime(2026, 12, 31),
                priority=8
            )
            
            # Content goals
            memory.set_goal(
                title="Publish 365 Medium articles",
                description="Write and publish one article every day",
                category=GoalCategory.CONTENT.value,
                target_value=365,
                unit="articles",
                deadline=datetime(2026, 12, 31),
                priority=6
            )
            
            logger.info("Master goals initialized")
    
    def get_daily_tasks(self) -> List[Dict]:
        """Generate daily tasks based on active goals"""
        tasks = []
        active_goals = memory.get_active_goals()
        
        for goal in active_goals:
            remaining = goal.target_value - goal.current_value
            if goal.deadline:
                days_left = (goal.deadline - datetime.utcnow()).days
                if days_left > 0:
                    daily_target = remaining / days_left
                else:
                    daily_target = remaining
            else:
                daily_target = remaining / 30  # default 30 days
            
            if goal.category == GoalCategory.INCOME.value:
                tasks.append({
                    "type": "freelance",
                    "action": "apply_to_jobs",
                    "target": max(50, int(daily_target / 100)),  # 50 jobs minimum
                    "goal_id": goal.id
                })
                tasks.append({
                    "type": "trading",
                    "action": "check_opportunities",
                    "target": 1,
                    "goal_id": goal.id
                })
            
            elif goal.category == GoalCategory.SOCIAL.value:
                if "Twitter" in goal.title or "X" in goal.title:
                    tasks.append({
                        "type": "social",
                        "platform": "twitter",
                        "action": "post",
                        "target": 10,  # 10 tweets per day
                        "goal_id": goal.id
                    })
                    tasks.append({
                        "type": "social",
                        "platform": "twitter",
                        "action": "reply",
                        "target": 50,  # Reply guy strategy
                        "goal_id": goal.id
                    })
                    tasks.append({
                        "type": "social",
                        "platform": "twitter",
                        "action": "follow",
                        "target": 100,  # Follow people
                        "goal_id": goal.id
                    })
            
            elif goal.category == GoalCategory.CONTENT.value:
                if "Medium" in goal.title or "article" in goal.title.lower():
                    tasks.append({
                        "type": "content",
                        "platform": "medium",
                        "action": "write_article",
                        "target": 1,
                        "goal_id": goal.id
                    })
            
            elif goal.category == GoalCategory.LEARNING.value:
                tasks.append({
                    "type": "learning",
                    "action": "study",
                    "target": 2,  # 2 hours daily
                    "goal_id": goal.id
                })
        
        return tasks
    
    def report_progress(self, goal_id: int, value: float):
        """Report progress on a goal"""
        memory.update_goal_progress(goal_id, value)
    
    def get_priority_goal(self) -> Optional[Goal]:
        """Get the highest priority active goal"""
        goals = memory.get_active_goals()
        if goals:
            return goals[0]  # Already sorted by priority
        return None
    
    def calculate_urgency(self, goal: Goal) -> float:
        """Calculate urgency score (0-1) based on deadline proximity"""
        if not goal.deadline:
            return 0.5
        
        days_left = (goal.deadline - datetime.utcnow()).days
        progress = goal.current_value / goal.target_value if goal.target_value > 0 else 0
        
        # High urgency if deadline close and progress low
        if days_left <= 0:
            return 1.0
        elif days_left <= 7:
            return 0.9 - (progress * 0.3)
        elif days_left <= 30:
            return 0.7 - (progress * 0.2)
        else:
            return 0.5 - (progress * 0.2)


# Global goal manager
goals = GoalManager()
