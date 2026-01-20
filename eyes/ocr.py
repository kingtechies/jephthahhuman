import asyncio
import os
import subprocess
from pathlib import Path
from loguru import logger
from hands.browser import browser

class OCRReader:
    def __init__(self):
        pass
        
    async def read_image(self, image_path: str) -> str:
        # Try local tesseract first
        try:
            cmd = f"tesseract {image_path} stdout"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
            
        # Fallback to online OCR (free)
        # Using a simple online OCR service via browser if local fails
        # or just fail gracefully if strictly no api
        logger.warning("Local OCR failed or Tesseract not installed. Attempting online...")
        return await self._online_ocr(image_path)
        
    async def _online_ocr(self, image_path: str) -> str:
        # Simple browser automation to use a free OCR site
        try:
            await browser.goto("https://www.onlineocr.net/")
            
            # File input detection might vary, simplified flow:
            file_input = await browser.page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(image_path)
                await asyncio.sleep(2)
                
            # Click convert
            await browser.click_like_human('#MainContent_btnOcr')
            await asyncio.sleep(5)
            
            # Get text from textarea
            text = await browser.get_element_value('#MainContent_txtOutputNode')
            return text
        except Exception as e:
            logger.error(f"Online OCR failed: {e}")
            return ""

ocr = OCRReader()
