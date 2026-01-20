"""
Jephthah Task Planner
Autonomous task scheduling and prioritization
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import heapq
from enum import Enum

from loguru import logger

from brain.memory import memory
from brain.goals import goals, GoalCategory


class TaskPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    IDLE = 5


class Task:
    """Represents a task to be executed"""
    
    def __init__(self, name: str, task_type: str, action: str,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 target: str = None, details: Dict = None,
                 deadline: datetime = None, goal_id: int = None):
        self.name = name
        self.task_type = task_type
        self.action = action
        self.priority = priority
        self.target = target
        self.details = details or {}
        self.deadline = deadline
        self.goal_id = goal_id
        self.created_at = datetime.utcnow()
        self.attempts = 0
        self.max_attempts = 3
        self.status = "pending"
    
    def __lt__(self, other):
        # For priority queue: lower priority value = higher importance
        return self.priority.value < other.priority.value
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.task_type,
            "action": self.action,
            "priority": self.priority.name,
            "target": self.target,
            "details": self.details,
            "status": self.status
        }


class TaskScheduler:
    """Manages and schedules tasks"""
    
    def __init__(self):
        self.task_queue: List[Task] = []
        self.completed_today = 0
        self.daily_targets = {
            "social": 10,      # Social media actions
            "freelance": 50,   # Job applications
            "content": 1,      # Articles
            "learning": 2,     # Hours
            "email": 10,       # Emails processed
        }
        self.task_handlers: Dict[str, Callable] = {}
        
        logger.info("Task scheduler initialized")
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type"""
        self.task_handlers[task_type] = handler
    
    def add_task(self, task: Task):
        """Add a task to the queue"""
        heapq.heappush(self.task_queue, task)
        logger.debug(f"Task added: {task.name} (Priority: {task.priority.name})")
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next task to execute"""
        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            
            if task.attempts >= task.max_attempts:
                logger.warning(f"Task failed max attempts: {task.name}")
                continue
            
            return task
        
        return None
    
    def plan_day(self):
        """Generate tasks for the day based on goals"""
        logger.info("Planning daily tasks")
        
        daily_tasks = goals.get_daily_tasks()
        
        for task_info in daily_tasks:
            task_type = task_info.get("type")
            action = task_info.get("action")
            target = task_info.get("target", 1)
            
            # Create multiple tasks based on target
            for i in range(min(target, 10)):  # Cap at 10 per batch
                task = Task(
                    name=f"{task_type}_{action}_{i}",
                    task_type=task_type,
                    action=action,
                    priority=self._get_priority(task_type),
                    target=task_info.get("platform", ""),
                    goal_id=task_info.get("goal_id")
                )
                self.add_task(task)
        
        # Add routine tasks
        self._add_routine_tasks()
        
        logger.info(f"Planned {len(self.task_queue)} tasks for today")
    
    def _get_priority(self, task_type: str) -> TaskPriority:
        """Determine priority based on task type"""
        priorities = {
            "freelance": TaskPriority.HIGH,      # Money first
            "trading": TaskPriority.HIGH,        # Money
            "content": TaskPriority.MEDIUM,      # Long-term value
            "social": TaskPriority.MEDIUM,       # Growth
            "learning": TaskPriority.LOW,        # Improvement
            "email": TaskPriority.HIGH,          # Responsiveness
        }
        return priorities.get(task_type, TaskPriority.MEDIUM)
    
    def _add_routine_tasks(self):
        """Add recurring routine tasks"""
        # Check emails
        self.add_task(Task(
            name="check_emails",
            task_type="email",
            action="check_inbox",
            priority=TaskPriority.HIGH
        ))
        
        # Check Telegram
        self.add_task(Task(
            name="check_telegram",
            task_type="communication",
            action="check_messages",
            priority=TaskPriority.CRITICAL
        ))
        
        # Learning session
        self.add_task(Task(
            name="daily_learning",
            task_type="learning",
            action="browse_and_learn",
            priority=TaskPriority.LOW
        ))
    
    async def execute_task(self, task: Task) -> bool:
        """Execute a single task"""
        task.attempts += 1
        task.status = "running"
        
        handler = self.task_handlers.get(task.task_type)
        
        if not handler:
            logger.warning(f"No handler for task type: {task.task_type}")
            task.status = "skipped"
            return False
        
        try:
            result = await handler(task)
            task.status = "completed" if result else "failed"
            
            if result:
                self.completed_today += 1
                
                # Update goal progress if applicable
                if task.goal_id:
                    # TODO: Update goal progress
                    pass
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            task.status = "error"
            
            # Re-add to queue if attempts remaining
            if task.attempts < task.max_attempts:
                self.add_task(task)
            
            return False
    
    async def run_schedule(self, duration_hours: float = 24):
        """Run the scheduler for a duration"""
        logger.info(f"Starting scheduler for {duration_hours} hours")
        
        end_time = datetime.utcnow() + timedelta(hours=duration_hours)
        
        while datetime.utcnow() < end_time:
            task = self.get_next_task()
            
            if task:
                logger.info(f"Executing: {task.name}")
                await self.execute_task(task)
                
                # Small delay between tasks
                await asyncio.sleep(5)
            else:
                # No tasks, wait and plan more
                logger.info("No tasks in queue, waiting...")
                await asyncio.sleep(60)
                
                # Re-plan if needed
                if not self.task_queue:
                    self.plan_day()
        
        logger.info(f"Scheduler complete. Tasks done today: {self.completed_today}")
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            "pending_tasks": len(self.task_queue),
            "completed_today": self.completed_today,
            "next_task": self.task_queue[0].name if self.task_queue else None
        }


# Global scheduler instance
scheduler = TaskScheduler()
