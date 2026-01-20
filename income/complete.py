import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from hands.browser import browser
from eyes.perception import perception
from hands.human import visual_captcha


class VideoGenerator:
    def __init__(self):
        self.videos_created = []
        
    async def create_faceless_video(self, topic: str, duration_sec: int = 60) -> str:
        from brain.smart import smart
        
        script = await smart.ask(f"Write a {duration_sec} second video script about {topic}. Just narration text.")
        
        video_dir = Path("projects/videos")
        video_dir.mkdir(parents=True, exist_ok=True)
        
        script_file = video_dir / f"{topic.replace(' ', '_')}_script.txt"
        script_file.write_text(script)
        
        await browser.goto("https://www.canva.com/create/videos/")
        await asyncio.sleep(3)
        
        await browser.goto("https://www.veed.io/new")
        await asyncio.sleep(3)
        
        await browser.goto("https://www.kapwing.com/tools/make/video")
        await asyncio.sleep(3)
        
        video_path = str(video_dir / f"{topic.replace(' ', '_')}.mp4")
        self.videos_created.append(video_path)
        logger.info(f"Video script created: {script_file}")
        return str(script_file)
    
    async def download_stock_video(self, query: str, output_path: str) -> bool:
        await browser.goto(f"https://www.pexels.com/search/videos/{query}")
        await asyncio.sleep(2)
        
        video_links = await browser.get_all_links()
        for link in video_links:
            if "video" in link.get("href", ""):
                await browser.goto(link["href"])
                await asyncio.sleep(2)
                await perception.find_and_click("Free Download")
                await asyncio.sleep(5)
                return True
        return False
    
    async def create_tts_audio(self, text: str, output_path: str) -> bool:
        await browser.goto("https://ttsmp3.com/")
        await asyncio.sleep(2)
        
        await perception.find_and_type("text", text[:3000])
        await perception.find_and_click("Read")
        await asyncio.sleep(5)
        await perception.find_and_click("Download")
        await asyncio.sleep(3)
        
        return True


class VoiceSynthesis:
    def __init__(self):
        self.tts_services = [
            "https://ttsmp3.com/",
            "https://www.naturalreaders.com/online/",
            "https://freetts.com/",
        ]
        
    async def text_to_speech(self, text: str) -> str:
        await browser.goto(self.tts_services[0])
        await asyncio.sleep(2)
        
        await perception.find_and_type("text", text[:3000])
        await perception.find_and_click("Read")
        await asyncio.sleep(5)
        
        await perception.find_and_click("Download")
        await asyncio.sleep(3)
        
        logger.info(f"TTS created for: {text[:50]}...")
        return "audio_downloaded"
    
    async def speech_to_text(self, audio_path: str) -> str:
        await browser.goto("https://speech-to-text-demo.ng.bluemix.net/")
        await asyncio.sleep(2)
        return ""


class PlayStorePublisher:
    def __init__(self):
        self.apps_published = []
        
    async def login_google_play_console(self) -> bool:
        await browser.goto("https://play.google.com/console/")
        await asyncio.sleep(3)
        
        page_text = await browser.get_page_text()
        if "sign in" in page_text.lower():
            return False
        return True
    
    async def create_app_listing(self, app_name: str, description: str, screenshots: List[str]) -> bool:
        await browser.goto("https://play.google.com/console/develop/apps/create")
        await asyncio.sleep(2)
        
        await perception.find_and_type("app name", app_name)
        await perception.find_and_type("description", description)
        
        await perception.find_and_click("Create app")
        await asyncio.sleep(3)
        
        return True
    
    async def upload_apk(self, apk_path: str) -> bool:
        file_input = await browser.page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(apk_path)
            await asyncio.sleep(10)
            return True
        return False
    
    async def submit_for_review(self) -> bool:
        await perception.find_and_click("Submit for review")
        await asyncio.sleep(3)
        return True
    
    async def full_publish(self, app_name: str, apk_path: str, description: str) -> bool:
        if not await self.login_google_play_console():
            from voice.bestie import bestie
            await bestie.send("Need Google Play Console login. Please login and say 'done'")
            return False
        
        await self.create_app_listing(app_name, description, [])
        await self.upload_apk(apk_path)
        await self.submit_for_review()
        
        self.apps_published.append(app_name)
        logger.info(f"App submitted: {app_name}")
        return True


class FullEcommerce:
    def __init__(self):
        self.platforms = {}
        self.listings = []
        
    async def login_ebay(self) -> bool:
        await browser.goto("https://signin.ebay.com/")
        await asyncio.sleep(2)
        
        from config.settings import config
        await perception.find_and_type("email", config.identity.email)
        await perception.find_and_click("Continue")
        await asyncio.sleep(2)
        
        return True
    
    async def create_ebay_listing(self, title: str, description: str, price: float, images: List[str], category: str = "Electronics") -> bool:
        await browser.goto("https://www.ebay.com/sl/sell")
        await asyncio.sleep(2)
        
        await perception.find_and_type("title", title)
        await perception.find_and_click("list it")
        await asyncio.sleep(2)
        
        await perception.find_and_type("description", description)
        await perception.find_and_type("price", str(price))
        
        for img in images[:12]:
            file_input = await browser.page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(img)
                await asyncio.sleep(2)
        
        await perception.find_and_click("List it")
        await asyncio.sleep(3)
        
        self.listings.append({"platform": "ebay", "title": title, "price": price})
        logger.info(f"eBay listing: {title}")
        return True
    
    async def create_etsy_listing(self, title: str, description: str, price: float, images: List[str]) -> bool:
        await browser.goto("https://www.etsy.com/your/shops/me/tools/listings/create")
        await asyncio.sleep(2)
        
        for img in images[:10]:
            file_input = await browser.page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(img)
                await asyncio.sleep(2)
        
        await perception.find_and_type("title", title)
        await perception.find_and_type("description", description)
        await perception.find_and_type("price", str(price))
        
        await perception.find_and_click("Publish")
        await asyncio.sleep(3)
        
        self.listings.append({"platform": "etsy", "title": title, "price": price})
        return True
    
    async def publish_kindle_book(self, title: str, author: str, description: str, manuscript_path: str, cover_path: str, price: float = 2.99) -> bool:
        await browser.goto("https://kdp.amazon.com/")
        await asyncio.sleep(2)
        
        await perception.find_and_click("Create")
        await asyncio.sleep(2)
        
        await perception.find_and_type("title", title)
        await perception.find_and_type("author", author)
        await perception.find_and_type("description", description)
        
        manuscript_input = await browser.page.query_selector('input[accept*="doc"]')
        if manuscript_input:
            await manuscript_input.set_input_files(manuscript_path)
            await asyncio.sleep(5)
        
        cover_input = await browser.page.query_selector('input[accept*="image"]')
        if cover_input:
            await cover_input.set_input_files(cover_path)
            await asyncio.sleep(3)
        
        await perception.find_and_type("price", str(price))
        await perception.find_and_click("Publish")
        await asyncio.sleep(5)
        
        logger.info(f"Kindle book published: {title}")
        return True
    
    async def create_gumroad_product(self, name: str, description: str, price: float, file_path: str) -> bool:
        await browser.goto("https://gumroad.com/products/new")
        await asyncio.sleep(2)
        
        await perception.find_and_type("name", name)
        await perception.find_and_type("description", description)
        await perception.find_and_type("price", str(price))
        
        file_input = await browser.page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(file_path)
            await asyncio.sleep(5)
        
        await perception.find_and_click("Publish")
        await asyncio.sleep(3)
        
        return True


video_gen = VideoGenerator()
voice = VoiceSynthesis()
play_store = PlayStorePublisher()
ecommerce = FullEcommerce()
