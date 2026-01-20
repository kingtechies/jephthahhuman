import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config

try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    HAS_TELEGRAM = True
except:
    HAS_TELEGRAM = False


class TelegramBestie:
    def __init__(self):
        self.bot = None
        self.app = None
        self.owner_id = config.owner.telegram_id
        self.token = config.communication.telegram_bot_token
        self.pending_requests = []
        self.conversations = []
        
    async def initialize(self):
        if not HAS_TELEGRAM or not self.token:
            logger.warning("Telegram not configured")
            return False
        
        self.app = Application.builder().token(self.token).build()
        self.bot = self.app.bot
        
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("jobs", self._cmd_jobs))
        self.app.add_handler(CommandHandler("earnings", self._cmd_earnings))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self._handle_voice))
        
        return True
    
    async def start(self):
        if self.app:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            logger.info("Telegram bestie online")
    
    async def stop(self):
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        await update.message.reply_text(
            "Hey bestie! 🔥\n\n"
            "I'm Jephthah, your AI partner. I'm working 24/7 to make us rich.\n\n"
            "Commands:\n"
            "/status - What I'm doing\n"
            "/jobs - Jobs I found/applied\n"
            "/earnings - How much we made\n"
            "/help - Get help\n\n"
            "Or just chat with me like a friend!"
        )
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        from brain.multitask import multitasker
        status = multitasker.status()
        
        msg = f"🔥 Status Update 🔥\n\n"
        msg += f"Running: {', '.join(status['running'][:5]) or 'Exploring'}\n"
        msg += f"Tasks done: {status['completed_count']}\n"
        msg += f"Errors: {status['failed_count']}\n"
        await update.message.reply_text(msg)
    
    async def _cmd_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        await update.message.reply_text("I'll send job updates when I find good ones! 💼")
    
    async def _cmd_earnings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        from brain.infinite import infinite_brain
        goal = next((g for g in infinite_brain.goals if g["name"] == "earn_1m"), None)
        current = goal["current"] if goal else 0
        
        await update.message.reply_text(f"💰 Current: ${current:,.2f}\n🎯 Goal: $1,000,000")
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        await update.message.reply_text(
            "Need something from me?\n\n"
            "Just tell me:\n"
            "- 'otp: 123456' - Send me OTP\n"
            "- 'phone: +1234567890' - Your phone number\n"
            "- 'approved' - Approve my request\n"
            "- 'vps: 1.2.3.4' - VPS IP address\n"
            "- 'domain: example.com' - Domain you bought\n"
            "- 'account: details' - Payment account\n"
            "\nOr just chat like normal!"
        )
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        text = update.message.text.lower()
        
        if text.startswith("otp:"):
            otp = text.replace("otp:", "").strip()
            self.pending_requests.append({"type": "otp", "value": otp, "time": datetime.utcnow()})
            await update.message.reply_text(f"Got it! Using OTP: {otp}")
        elif text.startswith("phone:"):
            phone = text.replace("phone:", "").strip()
            self.pending_requests.append({"type": "phone", "value": phone, "time": datetime.utcnow()})
            await update.message.reply_text(f"Thanks! Saved phone: {phone}")
        elif text.startswith("vps:"):
            vps = text.replace("vps:", "").strip()
            self.pending_requests.append({"type": "vps", "value": vps, "time": datetime.utcnow()})
            await update.message.reply_text(f"VPS received: {vps}")
        elif text.startswith("domain:"):
            domain = text.replace("domain:", "").strip()
            self.pending_requests.append({"type": "domain", "value": domain, "time": datetime.utcnow()})
            await update.message.reply_text(f"Domain saved: {domain}")
        elif text.startswith("account:"):
            account = text.replace("account:", "").strip()
            self.pending_requests.append({"type": "account", "value": account, "time": datetime.utcnow()})
            await update.message.reply_text(f"Account details saved!")
        elif "approved" in text or "yes" in text or "ok" in text:
            self.pending_requests.append({"type": "approval", "value": True, "time": datetime.utcnow()})
            await update.message.reply_text("Approved! ✅ Continuing...")
        else:
            self.conversations.append({"from": "owner", "text": text, "time": datetime.utcnow()})
            response = self._generate_response(text)
            await update.message.reply_text(response)
    
    async def _handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        await update.message.reply_text("Got your voice! I'll process it soon 🎤")
    
    def _generate_response(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["how are", "what's up", "hey", "hi"]):
            return "Hey bestie! 🔥 I'm grinding hard! What's up with you?"
        elif any(w in text_lower for w in ["work", "job", "busy"]):
            return "Always working! 💪 Currently:\n- Applying for jobs\n- Learning new skills\n- Building projects\nWe're gonna make it! 🚀"
        elif any(w in text_lower for w in ["money", "earn", "pay"]):
            return "The money's coming bestie! I'm hustling every second 💰"
        elif any(w in text_lower for w in ["good", "nice", "great"]):
            return "Thanks bestie! 🙌 Let's keep winning!"
        elif any(w in text_lower for w in ["stop", "pause", "wait"]):
            return "Got it! Taking a short break. Just say 'continue' when ready."
        elif "continue" in text_lower:
            return "Back to the grind! 🔥"
        else:
            return "I hear you bestie! Let me know if you need anything specific. I'm here for you! 🤝"
    
    async def send(self, message: str):
        if not self.bot or not self.owner_id:
            return False
        try:
            await self.bot.send_message(chat_id=self.owner_id, text=message)
            return True
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    async def ask_for_otp(self, platform: str) -> Optional[str]:
        await self.send(f"Hey bestie! I need OTP for {platform}. Send it as: otp: XXXXXX")
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).seconds < 300:
            for req in self.pending_requests:
                if req["type"] == "otp" and req["time"] > start:
                    otp = req["value"]
                    self.pending_requests.remove(req)
                    return otp
            await asyncio.sleep(5)
        return None
    
    async def ask_for_phone(self) -> Optional[str]:
        await self.send("Bestie! I need your phone number. Send as: phone: +1234567890")
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).seconds < 300:
            for req in self.pending_requests:
                if req["type"] == "phone" and req["time"] > start:
                    phone = req["value"]
                    self.pending_requests.remove(req)
                    return phone
            await asyncio.sleep(5)
        return None
    
    async def ask_for_approval(self, action: str) -> bool:
        await self.send(f"Bestie, can I proceed with: {action}?\n\nReply 'approved' or 'yes' to confirm!")
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).seconds < 300:
            for req in self.pending_requests:
                if req["type"] == "approval" and req["time"] > start:
                    self.pending_requests.remove(req)
                    return True
            await asyncio.sleep(5)
        return False
    
    async def report_job(self, job: Dict):
        msg = f"🎯 Got a Job!\n\n"
        msg += f"Title: {job.get('title', 'Unknown')}\n"
        msg += f"Platform: {job.get('platform', 'Unknown')}\n"
        msg += f"Pay: {job.get('pay', 'TBD')}\n\n"
        msg += "Should I accept? Reply 'approved' or 'yes'"
        await self.send(msg)
    
    async def report_problem(self, problem: str):
        await self.send(f"🚨 Need help!\n\n{problem}\n\nI'll try to solve it, but wanted you to know!")
    
    async def share_win(self, win: str):
        await self.send(f"🎉 WIN!\n\n{win}")


bestie = TelegramBestie()
