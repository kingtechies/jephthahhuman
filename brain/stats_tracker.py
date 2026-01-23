"""
Jephthah Stats Tracker
Centralized tracking of all agent activities with daily summaries
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from config.settings import DATA_DIR


class StatsTracker:
    """Track all agent activities and generate reports"""
    
    def __init__(self):
        self.stats_file = DATA_DIR / "daily_stats.json"
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_stats()
    
    def _load_stats(self):
        """Load stats from disk"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    self.all_stats = json.load(f)
            else:
                self.all_stats = {}
        except:
            self.all_stats = {}
    
    def _save_stats(self):
        """Save stats to disk"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.all_stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")
    
    def _get_today_key(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    def _ensure_today(self):
        """Ensure today's stats exist"""
        today = self._get_today_key()
        if today not in self.all_stats:
            self.all_stats[today] = {
                "emails_sent": 0,
                "emails_received": 0,
                "emails_replied": 0,
                "jobs_found": 0,
                "jobs_applied": 0,
                "jobs_verified": 0,
                "leads_scraped": 0,
                "cold_emails_sent": 0,
                "tweets_posted": 0,
                "articles_written": 0,
                "linkedin_posts": 0,
                "invoices_created": 0,
                "forums_joined": 0,
                "errors": 0,
                "uptime_hours": 0,
                "start_time": datetime.utcnow().isoformat()
            }
    
    def track(self, metric: str, increment: int = 1):
        """Increment a metric for today"""
        self._ensure_today()
        today = self._get_today_key()
        
        if metric not in self.all_stats[today]:
            self.all_stats[today][metric] = 0
        
        self.all_stats[today][metric] += increment
        self._save_stats()
        logger.debug(f"📊 Tracked: {metric} +{increment}")
    
    def get_today(self) -> Dict:
        """Get today's stats"""
        self._ensure_today()
        return self.all_stats.get(self._get_today_key(), {})
    
    def get_total(self, metric: str) -> int:
        """Get total for a metric across all days"""
        total = 0
        for day_stats in self.all_stats.values():
            if isinstance(day_stats, dict):
                total += day_stats.get(metric, 0)
        return total
    
    def generate_daily_summary(self) -> str:
        """Generate a summary message for Telegram"""
        stats = self.get_today()
        today = self._get_today_key()
        
        # Calculate uptime
        start_time_str = stats.get("start_time")
        uptime_hours = 0
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                uptime_hours = (datetime.utcnow() - start_time).total_seconds() / 3600
            except:
                pass
        
        summary = f"""📊 **DAILY STATUS REPORT** ({today})

💼 **Jobs**
• Found: {stats.get('jobs_found', 0)}
• Applied: {stats.get('jobs_applied', 0)}
• Verified: {stats.get('jobs_verified', 0)}

📧 **Emails**
• Received: {stats.get('emails_received', 0)}
• Sent: {stats.get('emails_sent', 0)}
• Replied: {stats.get('emails_replied', 0)}
• Cold Outreach: {stats.get('cold_emails_sent', 0)}

📱 **Social**
• Tweets: {stats.get('tweets_posted', 0)}
• LinkedIn: {stats.get('linkedin_posts', 0)}
• Articles: {stats.get('articles_written', 0)}

🔍 **Growth**
• Leads Scraped: {stats.get('leads_scraped', 0)}
• Forums Joined: {stats.get('forums_joined', 0)}
• Invoices: {stats.get('invoices_created', 0)}

⏱️ Uptime: {uptime_hours:.1f} hours
⚠️ Errors: {stats.get('errors', 0)}

📈 **All-Time Totals**
• Jobs Applied: {self.get_total('jobs_applied')}
• Emails Sent: {self.get_total('emails_sent')}
• Cold Emails: {self.get_total('cold_emails_sent')}
"""
        return summary
    
    def generate_quick_status(self) -> str:
        """Quick status for bot responses"""
        stats = self.get_today()
        return f"Today: {stats.get('jobs_applied', 0)} jobs applied, {stats.get('emails_sent', 0)} emails sent, {stats.get('cold_emails_sent', 0)} cold emails"


# Global stats tracker
stats = StatsTracker()
