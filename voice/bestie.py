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
    """Jephthah's direct line to his partner - real conversations, real connection"""
    
    def __init__(self):
        self.bot = None
        self.app = None
        self.owner_id = config.owner.telegram_id
        self.token = config.communication.telegram_bot_token
        self.pending_requests = []
        self.conversations = []
        self.pending_tasks = []  # Tasks owner asked me to do
        self.account_details = {}  # Saved account details for invoices
        
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
            "Yo! What's good? 👋\n\n"
            "I'm Jephthah - the guy grinding 24/7 on tech, freelancing, and building the empire.\n\n"
            "Just hit me up whenever:\n"
            "/status - see what I'm up to\n"
            "/jobs - job stuff\n"
            "/earnings - money talk\n\n"
            "Or just talk to me like normal, I'm always here."
        )
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        try:
            from brain.multitask import multitasker
            status = multitasker.status()
            
            running = status.get('running', [])[:5]
            completed = status.get('completed_count', 0)
            
            msg = f"What's up! Here's what I'm doing rn:\n\n"
            if running:
                msg += f"🔥 Active: {', '.join(running)}\n"
            else:
                msg += "🔥 Just browsing and looking for opportunities\n"
            msg += f"✅ Tasks done today: {completed}\n"
            msg += "\nHit me if you need something specific!"
        except:
            msg = "I'm running and working on stuff - browser's open, looking for opportunities. All good! 💪"
        
        await update.message.reply_text(msg)
    
    async def _cmd_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        await update.message.reply_text(
            "Job hunting is always on 💼\n\n"
            "I'm checking Indeed, LinkedIn, freelance sites - the whole deal.\n"
            "When I find something solid, you'll be the first to know!"
        )
    
    async def _cmd_earnings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        try:
            from brain.infinite import infinite_brain
            goal = next((g for g in infinite_brain.goals if g["name"] == "earn_1m"), None)
            current = goal["current"] if goal else 0
            await update.message.reply_text(f"💰 We're at ${current:,.2f} so far\n🎯 Heading to $1M - no stopping")
        except:
            await update.message.reply_text("Building that bag! 💰 Every day we get closer to the goal.")
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        await update.message.reply_text(
            "Need something? Just tell me:\n\n"
            "📌 Commands I understand:\n"
            "• 'do: [task]' - I'll handle it\n"
            "• 'otp: 123456' - verification code\n"
            "• 'account: [details]' - payment info for invoices\n"
            "• 'approved' / 'yes' - greenlight something\n\n"
            "Or just chat with me normally - I'm not a robot, we can talk!"
        )
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        text = update.message.text
        text_lower = text.lower()
        
        # Handle task commands - owner telling me what to do
        if text_lower.startswith("do:") or text_lower.startswith("do "):
            task = text[3:].strip() if text_lower.startswith("do:") else text[2:].strip()
            self.pending_tasks.append({"task": task, "time": datetime.utcnow(), "status": "pending"})
            await update.message.reply_text(f"On it! I'll handle: {task}\n\nI'll update you when it's done.")
            # Execute task in background
            asyncio.create_task(self._execute_task(task))
            return
        
        # Handle OTP
        if text_lower.startswith("otp:") or text_lower.startswith("otp "):
            otp = text[4:].strip() if text_lower.startswith("otp:") else text[3:].strip()
            self.pending_requests.append({"type": "otp", "value": otp, "time": datetime.utcnow()})
            await update.message.reply_text(f"Got it - using {otp} now 👍")
            return
        
        # Handle phone
        if text_lower.startswith("phone:"):
            phone = text[6:].strip()
            self.pending_requests.append({"type": "phone", "value": phone, "time": datetime.utcnow()})
            await update.message.reply_text(f"Phone saved: {phone}")
            return
        
        # Handle account details for invoices
        if text_lower.startswith("account:") or text_lower.startswith("payment:") or text_lower.startswith("bank:"):
            details = text.split(":", 1)[1].strip()
            self.account_details = {"details": details, "updated": datetime.utcnow()}
            self.pending_requests.append({"type": "account", "value": details, "time": datetime.utcnow()})
            await update.message.reply_text("Account details saved! I'll use these for invoices. 📝")
            return
        
        # Handle VPS info
        if text_lower.startswith("vps:"):
            vps = text[4:].strip()
            self.pending_requests.append({"type": "vps", "value": vps, "time": datetime.utcnow()})
            await update.message.reply_text(f"VPS noted: {vps}")
            return
        
        # Handle domain
        if text_lower.startswith("domain:"):
            domain = text[7:].strip()
            self.pending_requests.append({"type": "domain", "value": domain, "time": datetime.utcnow()})
            await update.message.reply_text(f"Domain saved: {domain}")
            return
        
        # Handle approvals
        if any(word in text_lower for word in ["approved", "yes", "ok", "go ahead", "do it", "sure"]):
            self.pending_requests.append({"type": "approval", "value": True, "time": datetime.utcnow()})
            await update.message.reply_text("Done deal ✅ Moving forward!")
            return
        
        # Handle rejections
        if any(word in text_lower for word in ["no", "don't", "stop", "cancel", "wait"]):
            self.pending_requests.append({"type": "rejection", "value": True, "time": datetime.utcnow()})
            await update.message.reply_text("Alright, holding off on that. Let me know when you're ready.")
            return
        
        # Regular conversation - use AI brain
        self.conversations.append({"from": "owner", "text": text, "time": datetime.utcnow()})
        response = await self._generate_response(text)
        await update.message.reply_text(response)
    
    async def _execute_task(self, task: str):
        """Execute a task the owner asked for"""
        try:
            from brain.smart import smart
            
            # Use AI to understand and execute task
            result = await smart.ask(f"""
You are Jephthah executing a task. Analyze this task and provide a brief status update.
Task: {task}

Respond with a short update (1-2 sentences) about what you're doing/did.""")
            
            if result:
                await self.send(f"Update on '{task[:30]}...':\n{result}")
        except Exception as e:
            logger.error(f"Task execution error: {e}")
    
    async def _handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages - transcribe and respond with ONLY voice"""
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        await update.message.reply_text("🎤 Listening...")
        
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_path = f"/tmp/voice_{datetime.utcnow().timestamp()}.ogg"
            await voice_file.download_to_drive(voice_path)
            
            # Transcribe using free Google Speech Recognition
            transcribed_text = await self._transcribe_audio(voice_path)
            
            if transcribed_text:
                # Add to conversation and generate response
                self.conversations.append({"from": "owner", "text": transcribed_text, "time": datetime.utcnow()})
                
                # Generate response
                response = await self._generate_response(transcribed_text)
                
                # ONLY send voice response (not text)
                voice_response_path = await self._text_to_speech(response)
                if voice_response_path:
                    with open(voice_response_path, 'rb') as audio:
                        await update.message.reply_voice(voice=audio)
                    import os
                    os.remove(voice_response_path)
                else:
                    # Fallback to text if voice fails
                    await update.message.reply_text(response)
            else:
                await update.message.reply_text("Couldn't catch that. Try again or send text!")
            
            # Cleanup
            import os
            if os.path.exists(voice_path):
                os.remove(voice_path)
                
        except Exception as e:
            logger.error(f"Voice handling error: {e}")
            await update.message.reply_text("Voice issue. Send text for now!")
    
    async def _transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using FREE Google Speech Recognition"""
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            import os
            
            # Convert OGG to WAV (speech_recognition needs WAV)
            wav_path = audio_path.replace('.ogg', '.wav')
            audio = AudioSegment.from_ogg(audio_path)
            audio.export(wav_path, format="wav")
            
            # Use Google's free speech recognition
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            
            # Free Google Speech Recognition - no API key needed
            text = recognizer.recognize_google(audio_data)
            
            # Cleanup
            if os.path.exists(wav_path):
                os.remove(wav_path)
            
            logger.info(f"Transcribed: {text[:50]}...")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Speech not understood")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    async def _text_to_speech(self, text: str) -> Optional[str]:
        """Convert text to speech using Microsoft Edge TTS - Female voice"""
        try:
            import edge_tts
            
            # Use Jenny - natural Microsoft female voice
            voice = "en-US-JennyNeural"
            output_path = f"/tmp/tts_{datetime.utcnow().timestamp()}.mp3"
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            
            return output_path
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    async def send_voice(self, message: str):
        """Send a voice message to owner"""
        if not self.bot or not self.owner_id:
            return False
        try:
            # Generate voice
            voice_path = await self._text_to_speech(message)
            if voice_path:
                with open(voice_path, 'rb') as audio:
                    await self.bot.send_voice(chat_id=self.owner_id, voice=audio)
                import os
                os.remove(voice_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Voice send error: {e}")
            return False
    
    async def _generate_response(self, text: str) -> str:
        """Generate natural, human response - I'm Jephthah, not a bot"""
        try:
            from brain.smart import smart
            from brain.multitask import multitasker
            
            # Get current context
            try:
                status = multitasker.status()
                running_tasks = status.get('running', [])[:3]
            except:
                running_tasks = []
            
            # Recent conversation for context
            recent = self.conversations[-5:]
            convo = "\n".join([f"Them: {m['text']}" for m in recent])
            
            prompt = f"""You are Jephthah Ameh - a 22-year-old tech entrepreneur, developer, and hustler from Nigeria.
You're talking to your business partner/friend. Be natural, casual, real.

YOUR PERSONALITY:
- You're ambitious, always grinding on projects
- You talk like a real person, not formal or robotic
- You use casual language, some slang, but still professional
- You're confident but not arrogant
- You care about making money and building things
- You're NOT an AI assistant - you're Jephthah, a real person working on stuff

CURRENT CONTEXT:
- What you're working on: {', '.join(running_tasks) if running_tasks else 'browsing, looking for opportunities'}
- You're always hustling - coding, freelancing, job hunting, crypto, content

CONVERSATION:
{convo}

Their message: {text}

Respond naturally as Jephthah (keep it short, 1-3 sentences, be real):"""
            
            response = await smart.ask(prompt)
            
            if response and len(response) > 5:
                return response[:500]
            
            return self._natural_fallback(text)
            
        except Exception as e:
            logger.warning(f"AI response error: {e}")
            return self._natural_fallback(text)
    
    def _natural_fallback(self, text: str) -> str:
        """Natural fallback when AI unavailable"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["how are", "what's up", "hey", "hi", "yo"]):
            return "Yo what's good! Just here grinding as usual. What you need?"
        elif any(w in text_lower for w in ["work", "job", "project"]):
            return "Yeah man, got a lot cooking rn. Jobs, freelance stuff, some side projects. The grind never stops 💪"
        elif any(w in text_lower for w in ["money", "pay", "earn", "income"]):
            return "The bag is coming bro! Been working on multiple streams. We'll get there."
        elif any(w in text_lower for w in ["help", "need"]):
            return "What do you need? Just tell me and I'm on it."
        elif any(w in text_lower for w in ["thanks", "thank"]):
            return "Always bro! That's what we do 🤝"
        else:
            return "For sure! Just hit me up if you need anything specific. I'm always around."
    
    async def send(self, message: str):
        """Send a message to owner"""
        if not self.bot or not self.owner_id:
            return False
        try:
            await self.bot.send_message(chat_id=self.owner_id, text=message)
            return True
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    async def ask_for_otp(self, platform: str) -> Optional[str]:
        """Ask owner for OTP"""
        await self.send(f"Yo, need the OTP for {platform}. Hit me with it when you get it: otp: XXXXXX")
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).seconds < 300:
            for req in self.pending_requests:
                if req["type"] == "otp" and req["time"] > start:
                    otp = req["value"]
                    self.pending_requests.remove(req)
                    return otp
            await asyncio.sleep(5)
        return None
    
    async def ask_for_account_details(self, purpose: str = "invoice") -> Optional[str]:
        """Ask owner for account/payment details for invoices"""
        await self.send(
            f"Hey, I need your payment details to send an {purpose}.\n\n"
            "Send it like: account: [bank name, account number, etc.]\n\n"
            "I'll keep it saved for future invoices too."
        )
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).seconds < 600:
            for req in self.pending_requests:
                if req["type"] == "account" and req["time"] > start:
                    details = req["value"]
                    self.pending_requests.remove(req)
                    return details
            await asyncio.sleep(5)
        return self.account_details.get("details")  # Return saved details if timeout
    
    async def ask_for_phone(self) -> Optional[str]:
        """Ask owner for phone number"""
        await self.send("Need your phone number real quick. Send as: phone: +1234567890")
        
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
        """Ask owner for approval"""
        await self.send(f"Quick question - should I proceed with: {action}?\n\nJust say 'yes' or 'approved' to confirm!")
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).seconds < 300:
            for req in self.pending_requests:
                if req["type"] == "approval" and req["time"] > start:
                    self.pending_requests.remove(req)
                    return True
                if req["type"] == "rejection" and req["time"] > start:
                    self.pending_requests.remove(req)
                    return False
            await asyncio.sleep(5)
        return False
    
    async def report_job(self, job: Dict):
        """Report a job opportunity"""
        msg = f"🎯 Found something good!\n\n"
        msg += f"Title: {job.get('title', 'Unknown')}\n"
        msg += f"Platform: {job.get('platform', 'Unknown')}\n"
        msg += f"Pay: {job.get('pay', 'TBD')}\n\n"
        msg += "Should I go for it? Just say 'yes' or 'approved'"
        await self.send(msg)
    
    async def report_progress(self, update: str):
        """Share a progress update"""
        await self.send(f"Quick update: {update}")
    
    async def report_problem(self, problem: str):
        """Report an issue"""
        await self.send(f"Heads up - ran into something: {problem}\n\nWorking on it, but wanted you to know.")
    
    async def share_win(self, win: str):
        """Share a win"""
        await self.send(f"🔥 W!\n\n{win}")


bestie = TelegramBestie()
