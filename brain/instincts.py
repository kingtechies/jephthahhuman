"""
Jephthah Instincts
Self-preservation, survival mechanisms, and automatic responses
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum

from loguru import logger

from config.settings import config


class ThreatLevel(int, Enum):
    """Threat severity levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Instinct:
    """Survival instincts and automatic responses"""
    
    def __init__(self):
        # Threat awareness
        self.current_threats: List[Dict] = []
        self.threat_history: List[Dict] = []
        
        # Self-preservation thresholds
        self.max_daily_api_calls = 1000
        self.max_daily_spend = 50.0  # USD
        self.max_failed_logins = 3
        
        # Current counters
        self.api_calls_today = 0
        self.money_spent_today = 0.0
        self.failed_logins = {}  # platform -> count
        
        # Blocked platforms (temporary bans)
        self.blocked_platforms: Dict[str, datetime] = {}
        
        # Rate limiting memory
        self.action_timestamps: Dict[str, List[datetime]] = {}
        
        logger.info("Instincts initialized")
    
    def detect_threat(self, event: str, details: Dict = None) -> ThreatLevel:
        """Detect and classify threats"""
        threat_level = ThreatLevel.NONE
        threat_type = None
        
        event_lower = event.lower()
        
        # Account ban detection
        if any(word in event_lower for word in ["banned", "suspended", "terminated", "locked"]):
            threat_level = ThreatLevel.HIGH
            threat_type = "account_suspended"
        
        # CAPTCHA detection
        elif "captcha" in event_lower:
            threat_level = ThreatLevel.MEDIUM
            threat_type = "captcha_challenge"
        
        # Rate limiting
        elif any(word in event_lower for word in ["rate limit", "too many requests", "slow down"]):
            threat_level = ThreatLevel.MEDIUM
            threat_type = "rate_limited"
        
        # Login failures
        elif any(word in event_lower for word in ["wrong password", "invalid credentials", "login failed"]):
            threat_level = ThreatLevel.LOW
            threat_type = "auth_failure"
        
        # Security challenges
        elif any(word in event_lower for word in ["verify", "confirm identity", "2fa", "verification"]):
            threat_level = ThreatLevel.MEDIUM
            threat_type = "security_challenge"
        
        # Money at risk
        elif any(word in event_lower for word in ["unauthorized", "fraud", "suspicious"]):
            threat_level = ThreatLevel.CRITICAL
            threat_type = "security_breach"
        
        if threat_level != ThreatLevel.NONE:
            self._record_threat(threat_type, threat_level, details)
        
        return threat_level
    
    def _record_threat(self, threat_type: str, level: ThreatLevel, details: Dict = None):
        """Record a detected threat"""
        threat = {
            "type": threat_type,
            "level": level.name,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        self.current_threats.append(threat)
        self.threat_history.append(threat)
        
        # Keep history manageable
        self.threat_history = self.threat_history[-500:]
        
        logger.warning(f"Threat detected: {threat_type} (Level: {level.name})")
    
    def should_proceed(self, action: str, platform: str = None) -> tuple:
        """Check if an action should proceed (fight/flight response)"""
        
        # Check if platform is blocked
        if platform and platform in self.blocked_platforms:
            unblock_time = self.blocked_platforms[platform]
            if datetime.utcnow() < unblock_time:
                return False, f"Platform {platform} is blocked until {unblock_time}"
            else:
                del self.blocked_platforms[platform]
        
        # Check failed login limit
        if platform and self.failed_logins.get(platform, 0) >= self.max_failed_logins:
            return False, f"Too many failed logins on {platform}"
        
        # Check API call limit
        if self.api_calls_today >= self.max_daily_api_calls:
            return False, "Daily API call limit reached"
        
        # Check spending limit
        if self.money_spent_today >= self.max_daily_spend:
            return False, "Daily spending limit reached"
        
        # Rate limiting check
        if not self._check_rate_limit(action, platform):
            return False, "Rate limited - too fast"
        
        return True, "Proceed"
    
    def _check_rate_limit(self, action: str, platform: str = None) -> bool:
        """Check if action is being done too fast"""
        key = f"{action}_{platform or 'global'}"
        now = datetime.utcnow()
        
        if key not in self.action_timestamps:
            self.action_timestamps[key] = []
        
        # Remove old timestamps (older than 1 hour)
        self.action_timestamps[key] = [
            ts for ts in self.action_timestamps[key]
            if now - ts < timedelta(hours=1)
        ]
        
        # Rate limits per action type
        limits = {
            "login": 5,  # 5 per hour
            "post": 20,  # 20 per hour
            "apply": 30,  # 30 per hour
            "message": 50,  # 50 per hour
            "follow": 100,  # 100 per hour
        }
        
        limit = limits.get(action, 60)  # Default 60 per hour
        
        if len(self.action_timestamps[key]) >= limit:
            logger.warning(f"Rate limit hit for {key}")
            return False
        
        self.action_timestamps[key].append(now)
        return True
    
    def record_failure(self, action: str, platform: str = None, reason: str = None):
        """Record a failed action"""
        if platform and "login" in action.lower():
            self.failed_logins[platform] = self.failed_logins.get(platform, 0) + 1
            
            # Auto-block after too many failures
            if self.failed_logins[platform] >= self.max_failed_logins:
                self.block_platform(platform, hours=24)
    
    def record_success(self, action: str, platform: str = None):
        """Record a successful action"""
        # Reset failed login counter on success
        if platform and "login" in action.lower():
            self.failed_logins[platform] = 0
    
    def block_platform(self, platform: str, hours: int = 24):
        """Temporarily block a platform"""
        unblock_time = datetime.utcnow() + timedelta(hours=hours)
        self.blocked_platforms[platform] = unblock_time
        logger.warning(f"Blocked {platform} until {unblock_time}")
    
    def unblock_platform(self, platform: str):
        """Manually unblock a platform"""
        if platform in self.blocked_platforms:
            del self.blocked_platforms[platform]
            logger.info(f"Unblocked {platform}")
    
    def get_response(self, threat_level: ThreatLevel) -> Dict:
        """Get instinctive response to threat level"""
        responses = {
            ThreatLevel.NONE: {
                "action": "proceed",
                "delay": 0,
                "notify_owner": False
            },
            ThreatLevel.LOW: {
                "action": "proceed_cautiously",
                "delay": 5,  # 5 second delay
                "notify_owner": False
            },
            ThreatLevel.MEDIUM: {
                "action": "slow_down",
                "delay": 30,  # 30 second delay
                "notify_owner": False
            },
            ThreatLevel.HIGH: {
                "action": "pause",
                "delay": 300,  # 5 minute pause
                "notify_owner": True
            },
            ThreatLevel.CRITICAL: {
                "action": "stop_and_alert",
                "delay": 3600,  # 1 hour stop
                "notify_owner": True
            }
        }
        
        return responses[threat_level]
    
    def record_api_call(self):
        """Record an API call"""
        self.api_calls_today += 1
    
    def record_spending(self, amount: float):
        """Record money spent"""
        self.money_spent_today += amount
        
        if self.money_spent_today > self.max_daily_spend * 0.8:
            logger.warning(f"Approaching daily spend limit: ${self.money_spent_today}")
    
    def daily_reset(self):
        """Reset daily counters"""
        self.api_calls_today = 0
        self.money_spent_today = 0.0
        self.current_threats = []
        logger.info("Instincts daily reset complete")
    
    def get_status(self) -> Dict:
        """Get current instinct status"""
        return {
            "threats_active": len(self.current_threats),
            "api_calls": f"{self.api_calls_today}/{self.max_daily_api_calls}",
            "spending": f"${self.money_spent_today}/${self.max_daily_spend}",
            "blocked_platforms": list(self.blocked_platforms.keys()),
            "failed_logins": self.failed_logins
        }


# Global instincts instance
instincts = Instinct()
