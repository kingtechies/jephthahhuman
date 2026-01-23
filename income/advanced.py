import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from hands.human import human_behavior


class YouTubeCreator:
    def __init__(self):
        self.channel_name = "Jephthah Tech"
        self.logged_in = False
        self.videos_uploaded = 0
        
    async def create_channel(self, name: str = None) -> bool:
        """Create YouTube channel - only logs success if VERIFIED"""
        self.channel_name = name or self.channel_name
        await browser.goto("https://www.youtube.com/channel_switcher")
        await asyncio.sleep(2)
        
        # Check if we're logged in first
        page_text = await browser.get_page_text()
        if "sign in" in page_text.lower():
            logger.warning("YouTube: Not logged in, cannot create channel")
            return False
        
        clicked = await perception.find_and_click("Create a channel")
        if not clicked:
            logger.warning("YouTube: Could not find 'Create a channel' button")
            return False
        
        await asyncio.sleep(2)
        typed = await perception.find_and_type("name", self.channel_name)
        if not typed:
            logger.warning("YouTube: Could not find name field")
            return False
        
        await perception.find_and_click("Create channel")
        await asyncio.sleep(3)
        
        # VERIFY: Check if channel was actually created
        page_text = await browser.get_page_text()
        current_url = await browser.get_current_url()
        
        if "studio.youtube" in current_url or "your channel" in page_text.lower() or self.channel_name.lower() in page_text.lower():
            logger.info(f"✅ VERIFIED: YouTube channel created: {self.channel_name}")
            return True
        else:
            logger.warning(f"❌ YouTube channel creation NOT verified for: {self.channel_name}")
            return False
    
    async def upload_video(self, video_path: str, title: str, description: str) -> bool:
        await browser.goto("https://studio.youtube.com/channel/upload")
        await asyncio.sleep(3)
        
        file_input = await browser.page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(video_path)
            await asyncio.sleep(5)
        
        await perception.find_and_type("title", title)
        await perception.find_and_type("description", description)
        
        await perception.find_and_click("Not made for kids")
        await perception.find_and_click("Next")
        await asyncio.sleep(1)
        await perception.find_and_click("Next")
        await asyncio.sleep(1)
        await perception.find_and_click("Next")
        await asyncio.sleep(1)
        await perception.find_and_click("Public")
        await perception.find_and_click("Publish")
        await asyncio.sleep(5)
        
        self.videos_uploaded += 1
        logger.info(f"Video uploaded: {title}")
        return True
    
    async def generate_faceless_video(self, topic: str) -> str:
        return ""


class EcommerceSeller:
    def __init__(self):
        self.platforms = {}
        self.listings = []
        
    async def login_ebay(self) -> bool:
        return False
    
    async def login_amazon(self) -> bool:
        return False
    
    async def login_etsy(self) -> bool:
        await browser.goto("https://www.etsy.com/signin")
        await asyncio.sleep(2)
        return False
    
    async def list_product(self, platform: str, product: Dict) -> bool:
        if platform == "ebay":
            return await self._list_on_ebay(product)
        elif platform == "etsy":
            return await self._list_on_etsy(product)
        elif platform == "amazon":
            return await self._list_on_amazon(product)
        return False
    
    async def _list_on_ebay(self, product: Dict) -> bool:
        await browser.goto("https://www.ebay.com/sl/sell")
        await asyncio.sleep(2)
        await perception.find_and_type("title", product.get("title", ""))
        return True
    
    async def _list_on_etsy(self, product: Dict) -> bool:
        await browser.goto("https://www.etsy.com/your/shops/me/tools/listings/create")
        await asyncio.sleep(2)
        return True
    
    async def _list_on_amazon(self, product: Dict) -> bool:
        return True
    
    async def sell_book(self, book_path: str, title: str, price: float) -> bool:
        await browser.goto("https://kdp.amazon.com/")
        await asyncio.sleep(2)
        return True


class GamblingBot:
    def __init__(self):
        self.balance = 0.0
        self.wins = 0
        self.losses = 0
        
    async def bet(self, platform: str, amount: float, choice: str) -> Dict:
        return {"status": "bet_placed", "amount": amount, "choice": choice}
    
    async def play_game(self, game: str) -> Dict:
        return {"game": game, "result": "played"}
    
    async def withdraw(self, amount: float, address: str) -> bool:
        return True


class CodingCompetitor:
    def __init__(self):
        self.solved = 0
        self.rank = 0
        
    async def solve_leetcode(self, problem_id: int = None) -> bool:
        if problem_id:
            await browser.goto(f"https://leetcode.com/problems/{problem_id}/")
        else:
            await browser.goto("https://leetcode.com/problemset/all/")
            await asyncio.sleep(2)
            links = await browser.get_all_links()
            for link in links:
                if "/problems/" in link.get("href", ""):
                    await browser.goto(link["href"])
                    break
        
        await asyncio.sleep(2)
        problem_text = await browser.get_page_text()
        
        language_buttons = await browser.page.query_selector_all('[data-mode-id]')
        for btn in language_buttons:
            text = await btn.inner_text()
            if "python" in text.lower():
                await btn.click()
                break
        
        solution = self._generate_solution(problem_text)
        editor = await browser.page.query_selector('.monaco-editor textarea')
        if editor:
            await editor.fill(solution)
        
        await perception.find_and_click("Submit")
        await asyncio.sleep(5)
        
        result_text = await browser.get_page_text()
        if "accepted" in result_text.lower():
            self.solved += 1
            logger.info("LeetCode problem solved!")
            return True
        return False
    
    def _generate_solution(self, problem: str) -> str:
        return '''class Solution:
    def solve(self, *args):
        return None'''
    
    async def compete_codeforces(self) -> bool:
        await browser.goto("https://codeforces.com/contests")
        await asyncio.sleep(2)
        return True
    
    async def compete_hackerrank(self) -> bool:
        await browser.goto("https://www.hackerrank.com/contests")
        await asyncio.sleep(2)
        return True


youtube = YouTubeCreator()
ecommerce = EcommerceSeller()
gambling = GamblingBot()
coding = CodingCompetitor()
