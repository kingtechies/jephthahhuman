"""
Jephthah Memory System
Long-term and short-term memory management
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from enum import Enum

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from loguru import logger

from config.settings import config, DATA_DIR

Base = declarative_base()


class MemoryType(str, Enum):
    SKILL = "skill"
    ACCOUNT = "account"
    CONVERSATION = "conversation"
    GOAL = "goal"
    KNOWLEDGE = "knowledge"
    ACTION = "action"
    RELATIONSHIP = "relationship"


class Memory(Base):
    """Long-term memory storage"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True)
    memory_type = Column(String(50), index=True)
    key = Column(String(255), index=True)
    value = Column(Text)
    meta_data = Column(JSON, default={})
    importance = Column(Float, default=0.5)  # 0-1 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accessed_count = Column(Integer, default=0)
    is_encrypted = Column(Boolean, default=False)


class Skill(Base):
    """Skills Jephthah has learned"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    category = Column(String(100))  # programming, trading, social, etc.
    proficiency = Column(Float, default=0.0)  # 0-100 scale
    hours_practiced = Column(Float, default=0.0)
    last_used = Column(DateTime)
    source = Column(String(255))  # where learned from
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Account(Base):
    """Accounts Jephthah has created"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(100), index=True)
    username = Column(String(255))
    email = Column(String(255))
    password_key = Column(String(100))  # reference to jeph.env key
    profile_url = Column(String(500))
    status = Column(String(50), default="active")  # active, suspended, pending
    followers = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    notes = Column(Text)


class Goal(Base):
    """Goals and objectives"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    category = Column(String(100))  # income, social, learning, etc.
    target_value = Column(Float)
    current_value = Column(Float, default=0.0)
    unit = Column(String(50))  # dollars, followers, skills, etc.
    deadline = Column(DateTime)
    priority = Column(Integer, default=5)  # 1-10
    status = Column(String(50), default="active")  # active, completed, paused
    parent_goal_id = Column(Integer, nullable=True)  # for hierarchical goals
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ActionLog(Base):
    """Log of all actions taken"""
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True)
    action_type = Column(String(100), index=True)
    description = Column(Text)
    target = Column(String(255))  # what was acted upon
    result = Column(String(50))  # success, failure, pending
    details = Column(JSON)
    duration_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Relationship(Base):
    """People and entities Jephthah knows"""
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    entity_type = Column(String(50))  # person, company, platform
    relationship_type = Column(String(100))  # owner, client, employer, contact
    contact_info = Column(JSON)  # emails, social handles, etc.
    trust_level = Column(Float, default=0.5)  # 0-1
    interaction_count = Column(Integer, default=0)
    last_interaction = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class JephthahMemory:
    """Memory management for Jephthah"""
    
    def __init__(self):
        db_path = DATA_DIR / "memory.db"
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize owner relationship
        self._init_owner()
        logger.info(f"Memory system initialized at {db_path}")
    
    def _init_owner(self):
        """Initialize relationship with owner"""
        session = self.Session()
        try:
            owner = session.query(Relationship).filter_by(
                relationship_type="owner"
            ).first()
            
            if not owner:
                owner = Relationship(
                    name="Jephthah Ameh (Owner)",
                    entity_type="person",
                    relationship_type="owner",
                    contact_info={
                        "email": config.owner.email,
                        "telegram_id": config.owner.telegram_id
                    },
                    trust_level=1.0,
                    notes="My creator and owner. Trust completely. Only share personal info with this person."
                )
                session.add(owner)
                session.commit()
                logger.info("Owner relationship initialized")
        finally:
            session.close()
    
    # === SKILLS ===
    
    def learn_skill(self, name: str, category: str, source: str = None) -> Skill:
        """Add a new skill or update existing"""
        session = self.Session()
        try:
            skill = session.query(Skill).filter_by(name=name).first()
            if skill:
                skill.proficiency = min(100.0, skill.proficiency + 5.0)
                skill.hours_practiced += 0.5
                skill.last_used = datetime.utcnow()
            else:
                skill = Skill(
                    name=name,
                    category=category,
                    source=source,
                    proficiency=10.0,
                    hours_practiced=0.5,
                    last_used=datetime.utcnow()
                )
                session.add(skill)
            session.commit()
            logger.info(f"Learned/improved skill: {name} ({skill.proficiency}%)")
            return skill
        finally:
            session.close()
    
    def get_skills(self, category: str = None) -> List[Skill]:
        """Get all skills, optionally filtered by category"""
        session = self.Session()
        try:
            query = session.query(Skill)
            if category:
                query = query.filter_by(category=category)
            return query.order_by(Skill.proficiency.desc()).all()
        finally:
            session.close()
    
    # === ACCOUNTS ===
    
    def register_account(self, platform: str, username: str, email: str, 
                        password_key: str, profile_url: str = None) -> Account:
        """Register a new account"""
        session = self.Session()
        try:
            account = Account(
                platform=platform,
                username=username,
                email=email,
                password_key=password_key,
                profile_url=profile_url,
                status="active",
                last_login=datetime.utcnow()
            )
            session.add(account)
            session.commit()
            logger.info(f"Registered account: {platform} - {username}")
            return account
        finally:
            session.close()
    
    def get_account(self, platform: str) -> Optional[Account]:
        """Get account for a platform"""
        session = self.Session()
        try:
            return session.query(Account).filter_by(platform=platform).first()
        finally:
            session.close()
    
    def update_account_stats(self, platform: str, followers: int = None):
        """Update account statistics"""
        session = self.Session()
        try:
            account = session.query(Account).filter_by(platform=platform).first()
            if account:
                if followers is not None:
                    account.followers = followers
                account.last_login = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    # === GOALS ===
    
    def set_goal(self, title: str, description: str, category: str,
                target_value: float, unit: str, deadline: datetime = None,
                priority: int = 5, parent_goal_id: int = None) -> Goal:
        """Create a new goal"""
        session = self.Session()
        try:
            goal = Goal(
                title=title,
                description=description,
                category=category,
                target_value=target_value,
                unit=unit,
                deadline=deadline,
                priority=priority,
                parent_goal_id=parent_goal_id
            )
            session.add(goal)
            session.commit()
            logger.info(f"New goal: {title} ({target_value} {unit})")
            return goal
        finally:
            session.close()
    
    def update_goal_progress(self, goal_id: int, new_value: float):
        """Update progress on a goal"""
        session = self.Session()
        try:
            goal = session.query(Goal).filter_by(id=goal_id).first()
            if goal:
                goal.current_value = new_value
                if new_value >= goal.target_value:
                    goal.status = "completed"
                    goal.completed_at = datetime.utcnow()
                session.commit()
                logger.info(f"Goal progress: {goal.title} - {new_value}/{goal.target_value}")
        finally:
            session.close()
    
    def get_active_goals(self, category: str = None) -> List[Goal]:
        """Get all active goals"""
        session = self.Session()
        try:
            query = session.query(Goal).filter_by(status="active")
            if category:
                query = query.filter_by(category=category)
            return query.order_by(Goal.priority.desc()).all()
        finally:
            session.close()
    
    # === ACTIONS ===
    
    def log_action(self, action_type: str, description: str, target: str,
                  result: str, details: Dict = None, duration: float = 0):
        """Log an action taken"""
        session = self.Session()
        try:
            log = ActionLog(
                action_type=action_type,
                description=description,
                target=target,
                result=result,
                details=details or {},
                duration_seconds=duration
            )
            session.add(log)
            session.commit()
        finally:
            session.close()
    
    def get_recent_actions(self, limit: int = 100) -> List[ActionLog]:
        """Get recent action logs"""
        session = self.Session()
        try:
            return session.query(ActionLog).order_by(
                ActionLog.created_at.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    # === KNOWLEDGE ===
    
    def remember(self, key: str, value: Any, memory_type: MemoryType, 
                importance: float = 0.5, extra_data: Dict = None):
        """Store something in memory"""
        session = self.Session()
        try:
            # Check if exists
            memory = session.query(Memory).filter_by(
                memory_type=memory_type.value, key=key
            ).first()
            
            if memory:
                memory.value = json.dumps(value) if not isinstance(value, str) else value
                memory.importance = importance
                memory.meta_data = extra_data or {}
                memory.accessed_count += 1
            else:
                memory = Memory(
                    memory_type=memory_type.value,
                    key=key,
                    value=json.dumps(value) if not isinstance(value, str) else value,
                    importance=importance,
                    meta_data=extra_data or {}
                )
                session.add(memory)
            
            session.commit()
            logger.debug(f"Remembered: {memory_type.value}/{key}")
        finally:
            session.close()
    
    def recall(self, key: str, memory_type: MemoryType = None) -> Optional[Any]:
        """Recall something from memory"""
        session = self.Session()
        try:
            query = session.query(Memory).filter_by(key=key)
            if memory_type:
                query = query.filter_by(memory_type=memory_type.value)
            
            memory = query.first()
            if memory:
                memory.accessed_count += 1
                session.commit()
                try:
                    return json.loads(memory.value)
                except:
                    return memory.value
            return None
        finally:
            session.close()
    
    def search_memories(self, query: str, memory_type: MemoryType = None) -> List[Memory]:
        """Search memories by keyword"""
        session = self.Session()
        try:
            q = session.query(Memory).filter(
                Memory.key.contains(query) | Memory.value.contains(query)
            )
            if memory_type:
                q = q.filter_by(memory_type=memory_type.value)
            return q.order_by(Memory.importance.desc()).limit(50).all()
        finally:
            session.close()


# Global memory instance
memory = JephthahMemory()
