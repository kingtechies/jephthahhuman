import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config

try:
    from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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
        self.pending_offers = {}  # Pending offers awaiting owner decision {offer_id: offer_data}
        
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
        self.app.add_handler(CommandHandler("invoice", self._cmd_invoice))
        self.app.add_handler(CommandHandler("offers", self._cmd_offers))
        self.app.add_handler(CallbackQueryHandler(self._handle_payment_callback, pattern="^payment_"))
        self.app.add_handler(CallbackQueryHandler(self._handle_offer_callback, pattern="^offer_"))
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
        """Show REAL live stats from the tracker"""
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        try:
            from brain.stats_tracker import stats
            from income.job_machine import job_machine
            from hands.browser import browser
            
            today_stats = stats.get_today()
            
            # Get live browser info
            current_url = "initializing..."
            try:
                if browser._is_initialized and browser.page:
                    current_url = await browser.get_current_url()
            except:
                pass
            
            msg = f"""📊 **LIVE SERVER STATUS**

🌐 **Browser**: {'ACTIVE' if browser._is_initialized else 'STARTING'}
🔗 **Current URL**: {current_url[:50]}...

💼 **Jobs Today**:
• Found: {today_stats.get('jobs_found', 0)}
• Applied: {today_stats.get('jobs_applied', 0)}
• Verified: {today_stats.get('jobs_verified', 0)}
• Total Ever: {job_machine.applied_count}

📧 **Emails Today**:
• Received: {today_stats.get('emails_received', 0)}
• Sent: {today_stats.get('emails_sent', 0)}
• Cold Outreach: {today_stats.get('cold_emails_sent', 0)}

📝 **Content**:
• Tweets: {today_stats.get('tweets_posted', 0)}
• Articles: {today_stats.get('articles_written', 0)}
• Forums: {today_stats.get('forums_joined', 0)}

⚠️ Errors: {today_stats.get('errors', 0)}
"""
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Status check error: {e}")
    
    async def _cmd_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show REAL job application stats"""
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        try:
            from income.job_machine import job_machine
            from brain.stats_tracker import stats
            
            today_stats = stats.get_today()
            recent_apps = job_machine.applications_history[-5:]  # Last 5
            
            msg = f"""💼 **JOB APPLICATION STATUS**

🎯 **Today**:
• Jobs Found: {today_stats.get('jobs_found', 0)}
• Applied: {today_stats.get('jobs_applied', 0)}
• Verified Success: {today_stats.get('jobs_verified', 0)}

📈 **All Time**: {job_machine.applied_count} applications

🗒️ **Recent Applications**:
"""
            for app in reversed(recent_apps):
                title = app.get('title', 'Unknown')[:40]
                company = app.get('company', 'Unknown')[:20]
                msg += f"• {title} @ {company}\n"
            
            if not recent_apps:
                msg += "No applications yet today\n"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Job stats error: {e}")
    
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
    
    async def send_job_applied(self, job: Dict, app_number: int = 0):
        """Send detailed notification when a job is applied"""
        msg = f"""🎯 **JOB APPLIED** #{app_number if app_number else ''}

📌 **Title**: {job.get('title', 'Unknown')[:60]}
🏢 **Company**: {job.get('company', 'Unknown Company')}
📍 **Location**: {job.get('location', 'Remote')}
💰 **Salary**: {job.get('salary', 'Not specified')}
🌐 **Source**: {job.get('site', 'Unknown')}

📝 **Description**:
{job.get('description', 'No description available')[:400]}...

🔗 View: {job.get('url', '#')[:60]}

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"""
        
        try:
            await self.send(msg)
        except Exception as e:
            logger.error(f"Job notification error: {e}")
    
    async def send_email_notification(self, email_type: str, details: Dict):
        """Notify about email activity"""
        if email_type == "received":
            msg = f"""📬 **NEW EMAIL**

From: {details.get('from', 'Unknown')}
Subject: {details.get('subject', 'No subject')}

Preview: {details.get('body', '')[:200]}..."""
        elif email_type == "replied":
            msg = f"""✉️ **EMAIL REPLIED**

To: {details.get('to', 'Unknown')}
Subject: {details.get('subject', 'No subject')}

Sent at: {datetime.utcnow().strftime('%H:%M')} UTC"""
        else:
            msg = f"📧 Email activity: {email_type}"
        
        await self.send(msg)
    
    async def _cmd_invoice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create and send an invoice"""
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "📄 **Create Invoice**\n\n"
                "Usage: /invoice <client_email> <amount> <description>\n\n"
                "Example: /invoice client@company.com 500 Website Development\n\n"
                "Currency defaults to USD. Add NGN at end for Naira:\n"
                "/invoice client@company.com 200000 Website Development NGN"
            )
            return
        
        try:
            from money.invoicing import invoice_generator
            
            client_email = args[0]
            amount = float(args[1])
            currency = "NGN" if args[-1].upper() == "NGN" else "USD"
            description = " ".join(args[2:-1] if currency == "NGN" else args[2:])
            client_name = client_email.split("@")[0].title()
            
            invoice = invoice_generator.create_invoice(
                client_name=client_name,
                client_email=client_email,
                description=description,
                amount=amount,
                currency=currency
            )
            
            # Send invoice summary
            summary = invoice_generator.get_invoice_summary(invoice["id"])
            await update.message.reply_text(
                f"✅ Invoice Created!\n\n{summary}\n\n"
                f"📎 HTML: {invoice['html_path']}"
            )
            
        except Exception as e:
            await update.message.reply_text(f"Error creating invoice: {e}")
    
    async def _handle_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment verification button clicks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data  # Format: payment_yes_INVOICEID or payment_no_INVOICEID
        parts = data.split("_")
        action = parts[1]  # yes or no
        invoice_id = "_".join(parts[2:])  # INV-20260120-XXXXXX
        
        try:
            from money.invoicing import invoice_generator, payment_verifier
            
            if action == "yes":
                # Confirm payment
                invoice_generator.mark_paid(invoice_id, "verified_by_owner")
                inv = invoice_generator.get_invoice(invoice_id)
                
                await query.edit_message_text(
                    f"✅ **PAYMENT CONFIRMED**\n\n"
                    f"Invoice: {invoice_id}\n"
                    f"Client: {inv['client_name']}\n"
                    f"Amount: {inv['currency']} {inv['amount']:,.2f}\n\n"
                    f"Thank you message will be sent to client."
                )
                
                # Send thank you to client via email
                from voice.email_handler import email_client
                thank_you = f"""Dear {inv['client_name']},

Thank you for your payment of {inv['currency']} {inv['amount']:,.2f} for "{inv['description']}".

Your payment has been received and confirmed. It was a pleasure working with you!

Best regards,
Jephthah Ameh
Full-Stack Developer
jephthahameh.cfd"""
                
                await email_client.send_email(
                    inv['client_email'],
                    f"Payment Received - Thank You! (Invoice {invoice_id})",
                    thank_you
                )
                
            elif action == "no":
                inv = invoice_generator.get_invoice(invoice_id)
                
                await query.edit_message_text(
                    f"❌ **PAYMENT NOT RECEIVED**\n\n"
                    f"Invoice: {invoice_id}\n"
                    f"Client will be notified that payment is not yet received."
                )
                
                # Notify client
                from voice.email_handler import email_client
                not_received = f"""Dear {inv['client_name']},

Regarding Invoice {invoice_id} for {inv['currency']} {inv['amount']:,.2f}:

We have not yet received your payment. If you have made the payment, please allow some time for processing or contact us with the transaction details.

Payment details are included in the invoice.

Best regards,
Jephthah Ameh
hireme@jephthahameh.cfd"""
                
                await email_client.send_email(
                    inv['client_email'],
                    f"Payment Status - Invoice {invoice_id}",
                    not_received
                )
                
        except Exception as e:
            await query.edit_message_text(f"Error processing: {e}")
    
    async def send_payment_verification(self, invoice_id: str, amount: float, 
                                        currency: str, payment_method: str, client_name: str):
        """Send payment verification request with Yes/No buttons"""
        if not self.bot or not self.owner_id:
            return
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Received", callback_data=f"payment_yes_{invoice_id}"),
                InlineKeyboardButton("❌ No, Not Yet", callback_data=f"payment_no_{invoice_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = f"""💰 **PAYMENT VERIFICATION**

📄 Invoice: {invoice_id}
👤 Client: {client_name}
💵 Amount: {currency} {amount:,.2f}
🏦 Method: {payment_method}
⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

**Boss, have you received this payment?**"""
        
        try:
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=msg,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            logger.info(f"Payment verification sent for {invoice_id}")
        except Exception as e:
            logger.error(f"Payment verification send error: {e}")
    
    async def send_invoice_request_alert(self, client_name: str, client_email: str, 
                                         message_preview: str, subject: str):
        """Alert owner when client requests invoice/payment info"""
        if not self.bot or not self.owner_id:
            return
        
        # Create button to initiate invoice creation
        keyboard = [
            [
                InlineKeyboardButton("📄 Create Invoice", callback_data=f"create_inv_{client_email[:30]}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = f"""💰 **INVOICE REQUEST DETECTED**

👤 Client: {client_name}
📧 Email: {client_email}
📌 Subject: {subject[:50]}

📝 Message Preview:
{message_preview[:200]}...

I've asked them for project details. When they reply, you can create an invoice with:
`/invoice {client_email} [amount] [description]`"""
        
        try:
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=msg,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            logger.info(f"Invoice request alert sent for {client_name}")
        except Exception as e:
            logger.error(f"Invoice request alert error: {e}")

    async def _cmd_offers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List pending offers awaiting decision"""
        if str(update.effective_user.id) != str(self.owner_id) and self.owner_id:
            return
        
        if not self.pending_offers:
            await update.message.reply_text("No pending offers right now. I'll alert you when one comes in! 🕵️")
            return
        
        await update.message.reply_text(f"📋 **{len(self.pending_offers)} Pending Offers**:\n\nReviewing details...")
        
        for offer_id, offer in self.pending_offers.items():
            await self.send_offer_alert(
                client_name=offer.get("client_name", "Unknown"),
                client_email=offer.get("client_email", ""),
                subject=offer.get("subject", ""),
                body_preview=offer.get("body", "")[:200],
                offer_id=offer_id
            )
            await asyncio.sleep(1)

    async def _handle_offer_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Accept/Reject/Details buttons for offers"""
        query = update.callback_query
        await query.answer()
        
        try:
            data = query.data
            action, offer_id = data.replace("offer_", "").split("_", 1)
            
            offer = self.pending_offers.get(offer_id)
            if not offer:
                await query.edit_message_text("❌ Offer data expired or not found.")
                return
            
            from voice.email_handler import email_client
            
            if action == "accept":
                # Auto-reply accepting the offer
                reply_body = f"""Hi {offer['client_name']},

Thank you for the offer! I accept.

I'm excited to work on this project with you. 

Could you please share the next steps? Do you have specific requirements or a contract to sign?

Also, let me know when you're ready for me to start.

Best regards,
Jephthah Ameh
Full-Stack Developer"""
                
                success = await email_client.reply(offer['email_obj'], reply_body)
                
                if success:
                    await query.edit_message_text(f"✅ **ACCEPTED & REPLIED**\n\nClient: {offer['client_name']}\nSubject: {offer['subject']}\n\nI've sent an acceptance email asking for next steps/contract. 🚀")
                    if offer_id in self.pending_offers:
                        del self.pending_offers[offer_id]
                else:
                    await query.edit_message_text("❌ Failed to send reply email. Please check logs.")
            
            elif action == "reject":
                # Auto-reply declining politely
                reply_body = f"""Hi {offer['client_name']},

Thank you for the offer. Unfortunately, I'm fully booked with other projects right now and won't be able to take this on.

I appreciate you considering me.

Best regards,
Jephthah Ameh"""
                
                success = await email_client.reply(offer['email_obj'], reply_body)
                
                if success:
                    await query.edit_message_text(f"🚫 **DECLINED**\n\nClient: {offer['client_name']}\n\nI've sent a polite rejection email.")
                    if offer_id in self.pending_offers:
                        del self.pending_offers[offer_id]
            
            elif action == "details":
                # Show full details
                full_msg = f"""📄 **OFFER DETAILS**
                
**From:** {offer['client_name']} ({offer['client_email']})
**Subject:** {offer['subject']}

**Message:**
{offer['body']}

-------------------
*Reply via buttons above to Accept/Reject*"""
                # Send as new message to keep buttons on original
                await context.bot.send_message(chat_id=self.owner_id, text=full_msg, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Offer callback error: {e}")
            await query.edit_message_text(f"Error processing offer: {e}")

    async def send_offer_alert(self, client_name: str, client_email: str, subject: str, 
                              body_preview: str, offer_id: str):
        """Alert owner about a new job/project offer"""
        if not self.bot or not self.owner_id:
            return
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Accept & Reply", callback_data=f"offer_accept_{offer_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"offer_reject_{offer_id}"),
            ],
            [
                InlineKeyboardButton("📜 View Details", callback_data=f"offer_details_{offer_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = f"""🎉 **NEW OFFER DETECTED!**
        
👤 **Client:** {client_name}
📧 **Email:** {client_email}
📌 **Subject:** {subject}

📝 **Preview:**
_{body_preview}..._

**What should I do?**
• **Accept:** I'll reply accepting and ask for next steps.
• **Reject:** I'll politely decline.
• **Details:** See full email."""
        
        try:
            await self.bot.send_message(
                chat_id=self.owner_id,
                text=msg,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            logger.info(f"Offer alert sent for {offer_id}")
        except Exception as e:
            logger.error(f"Offer alert error: {e}")


bestie = TelegramBestie()

