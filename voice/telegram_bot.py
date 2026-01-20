"""
Jephthah Telegram Bot
Real-time communication with owner
"""

import asyncio
from typing import Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger

from config.settings import config


class TelegramComm:
    """Telegram bot for owner communication"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.app: Optional[Application] = None
        self.owner_id: Optional[int] = None
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._is_running = False
        
        if config.owner.telegram_id:
            self.owner_id = int(config.owner.telegram_id)
        
        logger.info("Telegram communication initialized")
    
    async def initialize(self):
        """Initialize the bot"""
        token = config.communication.telegram_bot_token
        if not token:
            logger.warning("No Telegram bot token configured")
            return False
        
        self.app = Application.builder().token(token).build()
        self.bot = self.app.bot
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("status", self._handle_status))
        self.app.add_handler(CommandHandler("goals", self._handle_goals))
        self.app.add_handler(CommandHandler("actions", self._handle_actions))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self._handle_voice))
        
        logger.info("Telegram bot initialized")
        return True
    
    async def start(self):
        """Start the bot"""
        if self.app:
            await self.app.initialize()
            await self.app.start()
            self._is_running = True
            logger.info("Telegram bot started")
    
    async def stop(self):
        """Stop the bot"""
        if self.app:
            await self.app.stop()
            await self.app.shutdown()
            self._is_running = False
            logger.info("Telegram bot stopped")
    
    def _is_owner(self, user_id: int) -> bool:
        """Check if user is the owner"""
        return self.owner_id is not None and user_id == self.owner_id
    
    async def send_message(self, text: str, chat_id: int = None):
        """Send a message to owner"""
        target = chat_id or self.owner_id
        if target and self.bot:
            await self.bot.send_message(chat_id=target, text=text)
            logger.debug(f"Sent message to {target}")
    
    async def send_voice(self, audio_path: str, chat_id: int = None):
        """Send a voice message to owner"""
        target = chat_id or self.owner_id
        if target and self.bot:
            with open(audio_path, 'rb') as audio:
                await self.bot.send_voice(chat_id=target, voice=audio)
            logger.debug(f"Sent voice to {target}")
    
    async def notify_owner(self, message: str):
        """Send notification to owner"""
        await self.send_message(f"[JEPHTHAH] {message}")
    
    async def ask_owner(self, question: str) -> Optional[str]:
        """Ask owner a question and wait for response"""
        if not self.owner_id:
            logger.warning("No owner ID configured")
            return None
        
        await self.send_message(f"[QUESTION] {question}")
        
        # Wait for response (with timeout)
        try:
            response = await asyncio.wait_for(
                self._message_queue.get(),
                timeout=300  # 5 minutes
            )
            return response
        except asyncio.TimeoutError:
            logger.warning("Owner response timeout")
            return None
    
    # === HANDLERS ===
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        if not self._is_owner(user.id):
            await update.message.reply_text(
                "I only communicate with my owner. "
                "Please contact jephthahameh.cfd for business inquiries."
            )
            return
        
        # Save owner ID if not set
        if not self.owner_id:
            self.owner_id = user.id
            config.save_credential("OWNER_TELEGRAM_ID", str(user.id))
        
        await update.message.reply_text(
            f"Hello, {user.first_name}! I am Jephthah, your autonomous AI.\n\n"
            "Commands:\n"
            "/status - My current status\n"
            "/goals - View active goals\n"
            "/actions - Recent actions\n\n"
            "You can also send me voice notes!"
        )
    
    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._is_owner(update.effective_user.id):
            await update.message.reply_text("Unauthorized")
            return
        
        # TODO: Get actual status from brain
        status = (
            "JEPHTHAH STATUS\n"
            "===============\n"
            "State: Running\n"
            "Learning: Active\n"
            "Tasks Completed Today: 0\n"
            "Earnings Today: $0.00\n"
        )
        await update.message.reply_text(status)
    
    async def _handle_goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /goals command"""
        if not self._is_owner(update.effective_user.id):
            await update.message.reply_text("Unauthorized")
            return
        
        # TODO: Get actual goals from brain
        goals_text = (
            "ACTIVE GOALS\n"
            "============\n"
            "1. Earn $1,000,000 (2026) - 0%\n"
            "2. 1M Twitter followers - 0%\n"
            "3. 40+ active clients - 0%\n"
        )
        await update.message.reply_text(goals_text)
    
    async def _handle_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /actions command"""
        if not self._is_owner(update.effective_user.id):
            await update.message.reply_text("Unauthorized")
            return
        
        # TODO: Get actual actions from memory
        actions_text = (
            "RECENT ACTIONS\n"
            "==============\n"
            "No actions recorded yet.\n"
        )
        await update.message.reply_text(actions_text)
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user = update.effective_user
        text = update.message.text
        
        if not self._is_owner(user.id):
            await update.message.reply_text(
                "I only communicate with my owner. "
                "For business: hireme@jephthahameh.cfd"
            )
            return
        
        # Put message in queue for ask_owner
        await self._message_queue.put(text)
        
        # Acknowledge
        await update.message.reply_text(f"Received: {text[:50]}...")
        logger.info(f"Message from owner: {text[:100]}")
    
    async def _handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        user = update.effective_user
        
        if not self._is_owner(user.id):
            await update.message.reply_text("Unauthorized")
            return
        
        # Download voice file
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        voice_path = f"/tmp/voice_{voice.file_id}.ogg"
        await file.download_to_drive(voice_path)
        
        # TODO: Transcribe with Whisper
        await update.message.reply_text(
            "Voice received! (Transcription coming soon)"
        )
        logger.info(f"Voice message from owner saved: {voice_path}")


# Global telegram instance
telegram = TelegramComm()
