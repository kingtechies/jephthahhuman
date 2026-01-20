"""
Jephthah Twitter/X Automation
Growth hacking, posting, and engagement
"""

import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional

from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.vision import vision
from brain.memory import memory


class TwitterBot:
    """Twitter/X automation for growth and engagement"""
    
    def __init__(self):
        self.base_url = "https://x.com"
        self.logged_in = False
        self.daily_posts = 0
        self.max_daily_posts = 10  # User requested 10 posts per day
        
    async def login(self) -> bool:
        """Login to Twitter"""
        if self.logged_in:
            return True
        
        username = config.social.twitter_username
        password = config.social.twitter_password
        
        if not username or not password:
            logger.warning("Twitter credentials not configured")
            return False
        
        try:
            await browser.goto("https://x.com/login")
            await asyncio.sleep(2)
            
            # Enter username
            await browser.type_like_human('input[autocomplete="username"]', username)
            await browser.click_like_human('text=Next')
            await asyncio.sleep(1)
            
            # Enter password
            await browser.type_like_human('input[type="password"]', password)
            await browser.click_like_human('text=Log in')
            await asyncio.sleep(3)
            
            # Check if logged in
            if await vision.is_logged_in(["Home", "Profile", "Compose"]):
                self.logged_in = True
                logger.info("Twitter login successful")
                
                # Update account in memory
                account = memory.get_account("twitter")
                if not account:
                    memory.register_account(
                        platform="twitter",
                        username=username,
                        email=config.identity.email,
                        password_key="TWITTER_PASSWORD",
                        profile_url=f"https://x.com/{username}"
                    )
                
                return True
            else:
                logger.error("Twitter login failed")
                return False
                
        except Exception as e:
            logger.error(f"Twitter login error: {e}")
            return False
    
    async def post_tweet(self, content: str, media_path: str = None) -> bool:
        """Post a tweet"""
        if not await self.login():
            return False
        
        try:
            # Navigate to home
            await browser.goto("https://x.com/home")
            await asyncio.sleep(2)
            
            # Find the compose box
            compose_selector = '[data-testid="tweetTextarea_0"]'
            await browser.click_like_human(compose_selector)
            
            # Type the tweet
            await browser.type_like_human(compose_selector, content)
            await asyncio.sleep(1)
            
            # TODO: Handle media upload if provided
            
            # Click post button
            await browser.click_like_human('[data-testid="tweetButtonInline"]')
            await asyncio.sleep(2)
            
            logger.info(f"Tweet posted: {content[:50]}...")
            
            memory.log_action(
                action_type="social/tweet",
                description=f"Posted tweet",
                target="twitter",
                result="success",
                details={"content": content[:280]}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Tweet post error: {e}")
            return False
    
    async def reply_to_tweet(self, tweet_url: str, reply_text: str) -> bool:
        """Reply to a tweet (reply guy strategy)"""
        if not await self.login():
            return False
        
        try:
            await browser.goto(tweet_url)
            await asyncio.sleep(2)
            
            # Click reply button
            await browser.click_like_human('[data-testid="reply"]')
            await asyncio.sleep(1)
            
            # Type reply
            reply_box = '[data-testid="tweetTextarea_0"]'
            await browser.type_like_human(reply_box, reply_text)
            await asyncio.sleep(1)
            
            # Submit reply
            await browser.click_like_human('[data-testid="tweetButton"]')
            await asyncio.sleep(2)
            
            logger.info(f"Replied to tweet: {reply_text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Reply error: {e}")
            return False
    
    async def follow_user(self, username: str) -> bool:
        """Follow a user"""
        if not await self.login():
            return False
        
        try:
            await browser.goto(f"https://x.com/{username}")
            await asyncio.sleep(2)
            
            # Check if already following
            page_text = await browser.get_page_text()
            if "Following" in page_text:
                logger.info(f"Already following @{username}")
                return True
            
            # Click follow button
            follow_btn = '[data-testid="follow"]'
            await browser.click_like_human(follow_btn)
            await asyncio.sleep(1)
            
            logger.info(f"Followed @{username}")
            return True
            
        except Exception as e:
            logger.error(f"Follow error: {e}")
            return False
    
    async def like_tweet(self, tweet_url: str) -> bool:
        """Like a tweet"""
        if not await self.login():
            return False
        
        try:
            await browser.goto(tweet_url)
            await asyncio.sleep(2)
            
            await browser.click_like_human('[data-testid="like"]')
            await asyncio.sleep(1)
            
            logger.info(f"Liked tweet: {tweet_url}")
            return True
            
        except Exception as e:
            logger.error(f"Like error: {e}")
            return False
    
    async def retweet(self, tweet_url: str) -> bool:
        """Retweet a tweet"""
        if not await self.login():
            return False
        
        try:
            await browser.goto(tweet_url)
            await asyncio.sleep(2)
            
            await browser.click_like_human('[data-testid="retweet"]')
            await asyncio.sleep(0.5)
            await browser.click_like_human('[data-testid="retweetConfirm"]')
            await asyncio.sleep(1)
            
            logger.info(f"Retweeted: {tweet_url}")
            return True
            
        except Exception as e:
            logger.error(f"Retweet error: {e}")
            return False
    
    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for tweets"""
        if not await self.login():
            return []
        
        try:
            search_url = f"https://x.com/search?q={query}&f=live"
            await browser.goto(search_url)
            await asyncio.sleep(3)
            
            # Scroll to load more tweets
            for _ in range(3):
                await browser.scroll_like_human("down", 500)
                await asyncio.sleep(1)
            
            # Extract tweet links
            links = await browser.get_all_links()
            tweet_links = [
                link for link in links 
                if "/status/" in link.get("href", "")
            ][:limit]
            
            return tweet_links
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def get_followers_count(self) -> int:
        """Get current follower count"""
        if not await self.login():
            return 0
        
        try:
            username = config.social.twitter_username
            await browser.goto(f"https://x.com/{username}")
            await asyncio.sleep(2)
            
            # Try to find follower count
            # This is tricky as Twitter obfuscates selectors
            page_text = await browser.get_page_text()
            # TODO: Parse follower count from page
            
            return 0
            
        except Exception as e:
            logger.error(f"Get followers error: {e}")
            return 0
    
    async def reply_guy_strategy(self, hashtags: List[str], replies_count: int = 50):
        """Execute reply guy growth strategy"""
        replies_sent = 0
        
        for hashtag in hashtags:
            if replies_sent >= replies_count:
                break
            
            tweets = await self.search_tweets(f"#{hashtag}")
            
            for tweet in tweets[:10]:
                if replies_sent >= replies_count:
                    break
                
                tweet_url = tweet.get("href")
                if not tweet_url:
                    continue
                
                # Generate contextual reply
                reply = self._generate_reply(hashtag)
                
                success = await self.reply_to_tweet(tweet_url, reply)
                if success:
                    replies_sent += 1
                
                # Random delay between replies (2-5 minutes)
                await asyncio.sleep(random.randint(120, 300))
        
        logger.info(f"Reply guy: sent {replies_sent} replies")
        return replies_sent
    
    def _generate_reply(self, topic: str) -> str:
        """Generate a contextual reply"""
        templates = [
            f"Great point about #{topic}! Building something similar - would love to connect.",
            f"This is exactly what the #{topic} space needs. Let's discuss!",
            f"Insightful take on #{topic}. As a dev working in this area, I agree completely.",
            f"Love this perspective. #{topic} is definitely the future.",
            f"Facts! #{topic} is changing everything. What's your next move?",
        ]
        return random.choice(templates)
    
    async def daily_routine(self):
        """Execute daily Twitter growth routine"""
        logger.info("Starting Twitter daily routine")
        
        # Post 5-10 tweets
        tech_topics = [
            "AI is transforming how we build software. Here's what I learned today...",
            "Hot take: Most startups fail because they don't validate early enough.",
            "Building in public update: Making progress on my autonomous AI project.",
            "The future of work is async, remote, and AI-augmented. Adapt or get left behind.",
            "Crypto lesson learned: Always DYOR. Never trust, always verify.",
        ]
        
        for i, topic in enumerate(tech_topics[:random.randint(5, 10)]):
            await self.post_tweet(topic)
            await asyncio.sleep(random.randint(1800, 3600))  # 30-60 min between tweets
        
        # Reply guy strategy
        await self.reply_guy_strategy(
            hashtags=["AI", "Web3", "Crypto", "Startup", "BuildInPublic"],
            replies_count=50
        )
        
        # Follow relevant accounts
        # TODO: Implement strategic following
        
        logger.info("Twitter daily routine complete")


# Global Twitter bot instance
twitter = TwitterBot()
