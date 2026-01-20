"""
Jephthah Configuration Manager
Loads and manages all settings from jeph.env
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from cryptography.fernet import Fernet
from loguru import logger

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"

# Load environment
ENV_FILE = CONFIG_DIR / "jeph.env"
load_dotenv(ENV_FILE)


class OwnerConfig(BaseModel):
    """Owner communication settings"""
    email: str = os.getenv("OWNER_EMAIL", "kingblog242@gmail.com")
    telegram_id: Optional[str] = os.getenv("OWNER_TELEGRAM_ID")


class JephthahIdentity(BaseModel):
    """Jephthah's own identity"""
    name: str = "Jephthah"
    email: str = os.getenv("JEPHTHAH_EMAIL", "hireme@jephthahameh.cfd")
    email_password: Optional[str] = os.getenv("JEPHTHAH_EMAIL_PASSWORD")
    website: str = os.getenv("JEPHTHAH_WEBSITE", "https://jephthahameh.cfd")


class AIConfig(BaseModel):
    """AI provider configurations"""
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")


class CaptchaConfig(BaseModel):
    """CAPTCHA solving services"""
    twocaptcha_key: Optional[str] = os.getenv("TWOCAPTCHA_API_KEY")
    anticaptcha_key: Optional[str] = os.getenv("ANTICAPTCHA_API_KEY")


class SocialMediaConfig(BaseModel):
    """Social media credentials"""
    # Twitter
    twitter_api_key: Optional[str] = os.getenv("TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = os.getenv("TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_access_secret: Optional[str] = os.getenv("TWITTER_ACCESS_SECRET")
    twitter_username: Optional[str] = os.getenv("TWITTER_USERNAME")
    twitter_password: Optional[str] = os.getenv("TWITTER_PASSWORD")
    
    # Facebook
    facebook_email: Optional[str] = os.getenv("FACEBOOK_EMAIL")
    facebook_password: Optional[str] = os.getenv("FACEBOOK_PASSWORD")
    facebook_access_token: Optional[str] = os.getenv("FACEBOOK_ACCESS_TOKEN")
    
    # Instagram
    instagram_username: Optional[str] = os.getenv("INSTAGRAM_USERNAME")
    instagram_password: Optional[str] = os.getenv("INSTAGRAM_PASSWORD")
    
    # LinkedIn
    linkedin_email: Optional[str] = os.getenv("LINKEDIN_EMAIL")
    linkedin_password: Optional[str] = os.getenv("LINKEDIN_PASSWORD")
    
    # Medium
    medium_username: Optional[str] = os.getenv("MEDIUM_USERNAME")
    medium_password: Optional[str] = os.getenv("MEDIUM_PASSWORD")
    medium_token: Optional[str] = os.getenv("MEDIUM_TOKEN")


class FreelanceConfig(BaseModel):
    """Freelancing platform credentials"""
    upwork_email: Optional[str] = os.getenv("UPWORK_EMAIL")
    upwork_password: Optional[str] = os.getenv("UPWORK_PASSWORD")
    fiverr_email: Optional[str] = os.getenv("FIVERR_EMAIL")
    fiverr_password: Optional[str] = os.getenv("FIVERR_PASSWORD")
    freelancer_email: Optional[str] = os.getenv("FREELANCER_EMAIL")
    freelancer_password: Optional[str] = os.getenv("FREELANCER_PASSWORD")


class CryptoConfig(BaseModel):
    """Crypto and Web3 credentials"""
    eth_wallet: Optional[str] = os.getenv("ETH_WALLET_ADDRESS")
    eth_private_key: Optional[str] = os.getenv("ETH_PRIVATE_KEY")
    binance_api_key: Optional[str] = os.getenv("BINANCE_API_KEY")
    binance_secret: Optional[str] = os.getenv("BINANCE_SECRET")


class CommunicationConfig(BaseModel):
    """Communication settings"""
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    

class InfraConfig(BaseModel):
    """Infrastructure settings"""
    vps_ip: Optional[str] = os.getenv("VPS_IP")
    vps_password: Optional[str] = os.getenv("VPS_PASSWORD")
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    github_username: str = os.getenv("GITHUB_USERNAME", "kingtechies")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/memory.db")


class JephthahConfig:
    """Master configuration for Jephthah"""
    
    def __init__(self):
        self.owner = OwnerConfig()
        self.identity = JephthahIdentity()
        self.ai = AIConfig()
        self.captcha = CaptchaConfig()
        self.social = SocialMediaConfig()
        self.freelance = FreelanceConfig()
        self.crypto = CryptoConfig()
        self.communication = CommunicationConfig()
        self.infra = InfraConfig()
        
        # Encryption key for sensitive data
        self._fernet = None
        
        logger.info(f"Jephthah config loaded from {ENV_FILE}")
    
    def save_credential(self, key: str, value: str):
        """Save a new credential to jeph.env"""
        lines = []
        found = False
        
        if ENV_FILE.exists():
            with open(ENV_FILE, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    found = True
                    break
        
        if not found:
            lines.append(f"{key}={value}\n")
        
        with open(ENV_FILE, 'w') as f:
            f.writelines(lines)
        
        # Reload environment
        load_dotenv(ENV_FILE, override=True)
        logger.info(f"Saved credential: {key}")
    
    def is_personal_email(self, email: str) -> bool:
        """Check if email is the owner's personal email"""
        return email.lower() == self.owner.email.lower()
    
    def can_share_secrets_with(self, recipient: str) -> bool:
        """Security check: only share secrets with owner"""
        return self.is_personal_email(recipient)
    
    @property
    def openai_api_key(self) -> Optional[str]:
        return self.ai.openai_api_key
    
    @property
    def github_token(self) -> Optional[str]:
        return self.infra.github_token
    
    @property
    def github_username(self) -> str:
        return self.infra.github_username


# Global config instance
config = JephthahConfig()
