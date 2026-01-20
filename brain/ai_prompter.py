import asyncio
from datetime import datetime
from typing import Dict, List
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from hands.human import visual_captcha


class AIPrompter:
    def __init__(self):
        self.ai_platforms = {
            "gemini": "https://gemini.google.com",
            "chatgpt": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "perplexity": "https://www.perplexity.ai",
            "poe": "https://poe.com",
            "phind": "https://www.phind.com",
            "you": "https://you.com",
            "copilot": "https://copilot.microsoft.com",
        }
        self.logged_in = {}
        self.conversations = []
        
    async def prompt(self, query: str, platform: str = "gemini") -> str:
        url = self.ai_platforms.get(platform)
        if not url:
            return ""
        
        try:
            await browser.goto(url)
            await asyncio.sleep(3)
            
            if await visual_captcha.detect_captcha_type() != "none":
                await visual_captcha.solve()
            
            selectors = [
                'textarea[placeholder*="message" i]',
                'textarea[placeholder*="ask" i]',
                '[contenteditable="true"]',
                'textarea',
                '[role="textbox"]',
            ]
            
            for selector in selectors:
                try:
                    element = await browser.wait_for_selector(selector, timeout=3000)
                    if element:
                        await browser.type_like_human(selector, query)
                        break
                except:
                    continue
            
            await perception.find_and_click("Send")
            await perception.find_and_click("Submit")
            await browser.page.keyboard.press("Enter")
            
            await asyncio.sleep(10)
            
            response = await browser.get_page_text()
            
            self.conversations.append({
                "platform": platform,
                "query": query,
                "response": response[:2000],
                "time": datetime.utcnow().isoformat()
            })
            
            logger.info(f"AI prompt to {platform}: {query[:50]}...")
            return response[:5000]
            
        except Exception as e:
            logger.error(f"AI prompt error: {e}")
            return ""
    
    async def learn_from_ai(self, topic: str) -> str:
        query = f"Teach me everything about {topic}. Give me practical examples and code if relevant."
        
        for platform in ["gemini", "perplexity", "phind"]:
            response = await self.prompt(query, platform)
            if response and len(response) > 100:
                return response
        
        return ""
    
    async def get_solution(self, problem: str) -> str:
        query = f"How do I solve this problem: {problem}. Give me step by step solution."
        return await self.prompt(query, "perplexity")
    
    async def generate_code(self, description: str) -> str:
        query = f"Write complete code for: {description}. Use Python. Include all imports."
        return await self.prompt(query, "phind")
    
    async def research(self, topic: str) -> str:
        query = f"Research and give me comprehensive information about: {topic}"
        return await self.prompt(query, "perplexity")


class GitHubManager:
    def __init__(self):
        self.username = None
        self.repos = []
        
    async def create_account(self, email: str) -> bool:
        await browser.goto("https://github.com/signup")
        await asyncio.sleep(2)
        
        await perception.find_and_type("email", email)
        await perception.find_and_click("Continue")
        await asyncio.sleep(2)
        
        password = "Jeph" + "".join([chr(ord('a') + i % 26) for i in range(12)]) + "1!"
        await perception.find_and_type("password", password)
        await perception.find_and_click("Continue")
        await asyncio.sleep(2)
        
        username = f"jephthah{datetime.utcnow().strftime('%Y%m%d')}"
        await perception.find_and_type("username", username)
        await perception.find_and_click("Continue")
        await asyncio.sleep(2)
        
        if await visual_captcha.detect_captcha_type() != "none":
            await visual_captcha.solve()
        
        await perception.find_and_click("Create account")
        await asyncio.sleep(5)
        
        from voice.bestie import bestie
        otp = await bestie.ask_for_otp("GitHub")
        if otp:
            await perception.find_and_type("code", otp)
            await asyncio.sleep(3)
        
        self.username = username
        logger.info(f"GitHub account created: {username}")
        return True
    
    async def create_repo(self, name: str, description: str = "") -> bool:
        await browser.goto("https://github.com/new")
        await asyncio.sleep(2)
        
        await perception.find_and_type("repository", name)
        await perception.find_and_type("description", description)
        
        await perception.find_and_click("Public")
        await perception.find_and_click("Add a README")
        await perception.find_and_click("Create repository")
        await asyncio.sleep(3)
        
        self.repos.append({"name": name, "description": description})
        logger.info(f"Repo created: {name}")
        return True
    
    async def push_code(self, repo_name: str, files: Dict[str, str]) -> bool:
        return True
    
    async def commit(self, message: str) -> bool:
        return True


class EmailAccess:
    def __init__(self):
        self.email = "hireme@jephthahameh.cfd"
        self.logged_in = False
        
    async def login_webmail(self) -> bool:
        await browser.goto("https://mail.jephthahameh.cfd")
        await asyncio.sleep(2)
        
        await perception.find_and_type("email", self.email)
        await perception.find_and_type("username", self.email)
        
        from config.settings import config
        await perception.find_and_type("password", config.identity.email_password)
        
        await perception.find_and_click("Login")
        await perception.find_and_click("Sign in")
        await asyncio.sleep(3)
        
        self.logged_in = True
        return True
    
    async def check_inbox(self) -> List[Dict]:
        if not self.logged_in:
            await self.login_webmail()
        
        emails = []
        return emails
    
    async def reply_to_email(self, email_id: str, reply_text: str) -> bool:
        return True
    
    async def compose_email(self, to: str, subject: str, body: str) -> bool:
        await perception.find_and_click("Compose")
        await asyncio.sleep(1)
        
        await perception.find_and_type("to", to)
        await perception.find_and_type("subject", subject)
        await perception.find_and_type("body", body)
        
        await perception.find_and_click("Send")
        await asyncio.sleep(2)
        return True


ai_prompter = AIPrompter()
github_manager = GitHubManager()
email_access = EmailAccess()
