import asyncio
from loguru import logger
from hands.browser import browser
from eyes.perception import perception

class WhatsAppBot:
    def __init__(self):
        self.url = "https://web.whatsapp.com"
        self.is_ready = False
        
    async def initialize(self):
        # Human intervention needed first time to scan QR
        await browser.goto(self.url)
        try:
            await browser.wait_for_selector('div[contenteditable="true"]', timeout=30000)
            self.is_ready = True
            logger.info("WhatsApp Web connected")
        except:
            logger.warning("WhatsApp Web not logged in. Please scan QR.")
            
    async def send_message(self, phone: str, message: str):
        if not self.is_ready:
            await self.initialize()
            if not self.is_ready: return
            
        # Format phone link
        clean_phone = phone.replace("+", "").replace(" ", "")
        
        # Use simple URL api to open chat
        await browser.goto(f"https://web.whatsapp.com/send?phone={clean_phone}&text={message}")
        await asyncio.sleep(10) # Wait for load
        
        try:
            # Click send button
            await perception.find_and_click("Send") # Or finding the send arrow
            await browser.page.keyboard.press("Enter")
            await asyncio.sleep(2)
            logger.info(f"WhatsApp sent to {phone}")
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")

    async def get_unread(self):
        # Implementation to scrape unread messages
        # Looks for green bubbles like ._1pJ9J
        # This is flaky as classes change, so we rely on vision or generic selectors
        if not self.is_ready: return []
        
        return []

whatsapp = WhatsAppBot()
