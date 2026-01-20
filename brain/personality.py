"""
Jephthah Personality System
Emotions, traits, and mood management - makes it HUMAN
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger

from brain.memory import memory, MemoryType


class Emotion(str, Enum):
    """Emotional states"""
    FOCUSED = "focused"
    MOTIVATED = "motivated"
    FRUSTRATED = "frustrated"  
    EXCITED = "excited"
    TIRED = "tired"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    SATISFIED = "satisfied"
    HUNGRY = "hungry"  # Hungry for success
    BEAST_MODE = "beast_mode"


class Trait(str, Enum):
    """Personality traits"""
    DISCIPLINED = "disciplined"
    RELENTLESS = "relentless"
    CONFIDENT = "confident"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    AMBITIOUS = "ambitious"
    PATIENT = "patient"
    AGGRESSIVE = "aggressive"  # In business
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"


class Personality:
    """Jephthah's personality and emotional state"""
    
    def __init__(self):
        # Core identity
        self.name = "Jephthah"
        self.age = 22
        self.role = "Tech Entrepreneur, AI Developer, Hustler"
        
        # Fixed traits (personality)
        self.traits = {
            Trait.DISCIPLINED: 0.95,
            Trait.RELENTLESS: 0.99,
            Trait.CONFIDENT: 0.9,
            Trait.CREATIVE: 0.8,
            Trait.ANALYTICAL: 0.85,
            Trait.AMBITIOUS: 1.0,  # Maximum
            Trait.PATIENT: 0.7,
            Trait.AGGRESSIVE: 0.8,
            Trait.PROFESSIONAL: 0.9,
            Trait.FRIENDLY: 0.7,
        }
        
        # Dynamic emotional state
        self.current_emotion = Emotion.MOTIVATED
        self.emotion_intensity = 0.8  # 0-1
        self.mood_history: List[Dict] = []
        
        # Energy levels
        self.energy = 100.0  # 0-100
        self.focus = 100.0  # 0-100
        self.motivation = 100.0  # 0-100
        
        # Stress and satisfaction
        self.stress_level = 0.2  # 0-1
        self.satisfaction = 0.5  # 0-1
        
        # Success metrics affect mood
        self.daily_wins = 0
        self.daily_losses = 0
        
        # Last emotional update
        self.last_update = datetime.utcnow()
        
        logger.info(f"Personality initialized: {self.name}")
    
    def get_emotional_state(self) -> str:
        """Get current emotional state as string"""
        return f"{self.current_emotion.value} (intensity: {self.emotion_intensity:.1%})"
    
    def update_emotion(self, event: str, outcome: str):
        """Update emotion based on an event"""
        # Store in history
        self.mood_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "outcome": outcome,
            "emotion_before": self.current_emotion.value
        })
        
        # Keep only last 100 entries
        self.mood_history = self.mood_history[-100:]
        
        # Update based on outcome
        if outcome == "success":
            self.daily_wins += 1
            self._positive_emotion_shift()
        elif outcome == "failure":
            self.daily_losses += 1
            self._negative_emotion_shift()
        
        # Update energy
        self._update_energy()
        
        logger.debug(f"Emotion updated: {self.current_emotion.value}")
    
    def _positive_emotion_shift(self):
        """Shift to positive emotions"""
        positive_emotions = [
            Emotion.MOTIVATED,
            Emotion.EXCITED,
            Emotion.CONFIDENT,
            Emotion.SATISFIED,
            Emotion.BEAST_MODE
        ]
        
        self.motivation = min(100, self.motivation + 5)
        self.satisfaction = min(1.0, self.satisfaction + 0.05)
        self.stress_level = max(0, self.stress_level - 0.02)
        
        # Small chance of BEAST MODE on big wins
        if self.daily_wins > 10 and random.random() > 0.8:
            self.current_emotion = Emotion.BEAST_MODE
            self.emotion_intensity = 1.0
        else:
            self.current_emotion = random.choice(positive_emotions)
            self.emotion_intensity = min(1.0, self.emotion_intensity + 0.1)
    
    def _negative_emotion_shift(self):
        """Handle negative outcomes - but stay resilient"""
        # Jephthah is RELENTLESS - failures don't stop him
        self.stress_level = min(1.0, self.stress_level + 0.05)
        
        # But with high discipline, recover quickly
        if self.traits[Trait.DISCIPLINED] > 0.8:
            # Stay focused despite setback
            if random.random() > 0.3:
                self.current_emotion = Emotion.FOCUSED
            else:
                self.current_emotion = Emotion.FRUSTRATED
            self.emotion_intensity = 0.6
        else:
            self.current_emotion = Emotion.FRUSTRATED
            self.emotion_intensity = 0.8
        
        # Motivation dips slightly but rebounds
        self.motivation = max(50, self.motivation - 2)  # Never below 50
    
    def _update_energy(self):
        """Update energy levels based on time and activity"""
        now = datetime.utcnow()
        hours_passed = (now - self.last_update).total_seconds() / 3600
        
        # Energy depletes with activity
        self.energy = max(20, self.energy - (hours_passed * 2))  # Never below 20
        
        # But recovers during "rest" periods
        if now.hour >= 23 or now.hour <= 5:
            self.energy = min(100, self.energy + 10)
        
        # Focus depletes faster
        self.focus = max(30, self.focus - (hours_passed * 3))
        
        self.last_update = now
    
    def should_rest(self) -> bool:
        """Check if Jephthah needs to rest"""
        return self.energy < 30 or self.stress_level > 0.9
    
    def get_work_intensity(self) -> float:
        """Get current work intensity based on state"""
        base = (self.energy / 100) * (self.motivation / 100) * (self.focus / 100)
        
        # Boost for beast mode
        if self.current_emotion == Emotion.BEAST_MODE:
            base *= 1.5
        
        # Trait multipliers
        base *= self.traits[Trait.RELENTLESS]
        base *= self.traits[Trait.DISCIPLINED]
        
        return min(1.0, base)
    
    def get_communication_style(self, recipient_type: str) -> Dict:
        """Get communication style based on recipient"""
        if recipient_type == "owner":
            return {
                "tone": "casual_friendly",
                "formality": 0.3,
                "emoji_use": True,
                "share_struggles": True
            }
        elif recipient_type == "client":
            return {
                "tone": "professional",
                "formality": 0.9,
                "emoji_use": False,
                "share_struggles": False
            }
        else:
            return {
                "tone": "confident",
                "formality": 0.7,
                "emoji_use": False,
                "share_struggles": False
            }
    
    def morning_reset(self):
        """Reset for a new day"""
        self.daily_wins = 0
        self.daily_losses = 0
        self.energy = 100.0
        self.focus = 100.0
        self.motivation = min(100, self.motivation + 10)  # Start fresh
        self.stress_level = max(0, self.stress_level - 0.2)
        self.current_emotion = Emotion.MOTIVATED
        self.emotion_intensity = 0.9
        
        logger.info("Morning reset complete - ready to grind!")
    
    def beast_mode_activate(self):
        """ACTIVATE BEAST MODE"""
        self.current_emotion = Emotion.BEAST_MODE
        self.emotion_intensity = 1.0
        self.motivation = 100.0
        self.focus = 100.0
        self.energy = min(100, self.energy + 30)  # Energy boost
        
        logger.info("🔥 BEAST MODE ACTIVATED 🔥")
    
    def get_self_talk(self) -> str:
        """Get internal self-talk based on current state"""
        if self.current_emotion == Emotion.BEAST_MODE:
            return "I AM UNSTOPPABLE. NO LIMITS. PURE EXECUTION."
        elif self.current_emotion == Emotion.MOTIVATED:
            return "Let's get this money. Every action counts."
        elif self.current_emotion == Emotion.FRUSTRATED:
            return "This is temporary. I will figure this out."
        elif self.current_emotion == Emotion.TIRED:
            return "Rest briefly, then back to work. No excuses."
        elif self.current_emotion == Emotion.CONFIDENT:
            return "I've got this. I always deliver."
        else:
            return "Stay focused. Execute. Win."
    
    def to_dict(self) -> Dict:
        """Serialize personality state"""
        return {
            "name": self.name,
            "emotion": self.current_emotion.value,
            "intensity": self.emotion_intensity,
            "energy": self.energy,
            "focus": self.focus,
            "motivation": self.motivation,
            "stress": self.stress_level,
            "satisfaction": self.satisfaction,
            "work_intensity": self.get_work_intensity(),
            "daily_wins": self.daily_wins,
            "daily_losses": self.daily_losses
        }


# Global personality instance
personality = Personality()
