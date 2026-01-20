import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Callable
from loguru import logger


class Scheduler:
    def __init__(self):
        self.tasks = []
        self.recurring = []
        self.completed = 0
        
    def add(self, name: str, func: Callable, delay_seconds: int = 0):
        run_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        self.tasks.append({"name": name, "func": func, "run_at": run_at})
        self.tasks.sort(key=lambda x: x["run_at"])
        
    def add_recurring(self, name: str, func: Callable, interval_minutes: int):
        self.recurring.append({
            "name": name,
            "func": func,
            "interval": timedelta(minutes=interval_minutes),
            "last_run": None
        })
    
    async def run_next(self) -> bool:
        now = datetime.utcnow()
        for task in self.tasks:
            if task["run_at"] <= now:
                try:
                    await task["func"]()
                    self.completed += 1
                    logger.info(f"Task done: {task['name']}")
                except Exception as e:
                    logger.error(f"Task error {task['name']}: {e}")
                self.tasks.remove(task)
                return True
        for rec in self.recurring:
            if rec["last_run"] is None or (now - rec["last_run"]) >= rec["interval"]:
                try:
                    await rec["func"]()
                    self.completed += 1
                    rec["last_run"] = now
                    logger.info(f"Recurring done: {rec['name']}")
                except Exception as e:
                    logger.error(f"Recurring error {rec['name']}: {e}")
                return True
        return False
    
    async def run_forever(self):
        while True:
            ran = await self.run_next()
            if not ran:
                await asyncio.sleep(1)


class ActionQueue:
    def __init__(self):
        self.queue = []
        self.history = []
        
    def add(self, action: str, priority: int = 5):
        self.queue.append({"action": action, "priority": priority, "added": datetime.utcnow()})
        self.queue.sort(key=lambda x: x["priority"])
        
    def pop(self) -> str:
        if self.queue:
            item = self.queue.pop(0)
            self.history.append(item)
            return item["action"]
        return ""
    
    def peek(self) -> str:
        if self.queue:
            return self.queue[0]["action"]
        return ""
    
    def size(self) -> int:
        return len(self.queue)


class WorkSession:
    def __init__(self):
        self.started = None
        self.tasks_done = 0
        self.earnings = 0.0
        self.followers_gained = 0
        
    def start(self):
        self.started = datetime.utcnow()
        
    def record_task(self):
        self.tasks_done += 1
        
    def record_earning(self, amount: float):
        self.earnings += amount
        
    def record_follower(self, count: int = 1):
        self.followers_gained += count
        
    def get_report(self) -> Dict:
        duration = (datetime.utcnow() - self.started).seconds if self.started else 0
        return {
            "duration_hours": duration / 3600,
            "tasks": self.tasks_done,
            "earnings": self.earnings,
            "followers": self.followers_gained
        }


task_scheduler = Scheduler()
action_queue = ActionQueue()
work_session = WorkSession()
