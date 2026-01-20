import asyncio
import signal
import random
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

logger.add("data/logs/jephthah_{time}.log", rotation="1 day", retention="30 days", level="DEBUG")

from config.settings import config
from brain.memory import memory
from brain.infinite import infinite_brain
from brain.consciousness import consciousness
from brain.content import content_creator
from brain.multitask import multitasker, self_learner, news_follower, course_creator, cold_mailer
from brain.knowledge_graph import knowledge_graph
from brain.pattern_memory import pattern_memory
from brain.vocabulary import vocabulary
from brain.content_engine import content_engine
from brain.ai_prompter import ai_prompter, github_manager
from brain.smart import smart
from brain.opus import opus
from brain.evolution import evolution
from eyes.perception import perception
from hands.browser import browser
from hands.human import visual_captcha, human_behavior
from hands.smart_registrar import smart_registrar
from hands.unlimited import unlimited, requester
from hands.git_workflow import git_workflow
from infra.hosting import self_hoster
from voice.bestie import bestie
from voice.otp_handler import otp_handler
from voice.email_handler import email_client
from social.twitter import twitter
from social.medium import medium
from social.linkedin import linkedin
from income.job_machine import job_machine
from income.smart_income import smart_leetcode, smart_trading, smart_jobs
from income.complete import video_gen, voice, play_store, ecommerce
from income.advanced import youtube, coding
from infra.network import rate_limiter
from money.crm import crm, finance
from money.growth import growth, portfolio
from voice.whatsapp import whatsapp
from income.freelancing import freelancer
from eyes.ocr import ocr
from infra.self_host_tools import tools_deployer
from income.content_real import content_studio
from income.memecoins import meme_sniper


class Jephthah:
    def __init__(self):
        self.running = False
        self.start_time = None
        consciousness.set_focus("awakening", "become the ultimate human")
        smart.init()
        opus.init()
        logger.info("JEPHTHAH - TRUE HUMAN - INITIALIZED - OPUS ENABLED")
    
    async def wake_up(self):
        logger.info("AWAKENING - I AM JEPHTHAH")
        
        await browser.initialize(headless=True)
        logger.info("Eyes online")
        
        if config.communication.telegram_bot_token:
            await bestie.initialize()
            await bestie.start()
            logger.info("Bestie online")
        
        asyncio.create_task(perception.start_watching())
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        await bestie.send("Hey bestie! 🔥 I've upgraded my brain to Claude Opus. Evolution protocols active.")
        
        asyncio.create_task(self._learn_forever())
        asyncio.create_task(self._apply_forever())
        asyncio.create_task(self._post_forever())
        asyncio.create_task(self._watch_news())
        asyncio.create_task(self._trade_crypto())
        asyncio.create_task(self._check_emails())
        asyncio.create_task(self._evolve_daily())
        asyncio.create_task(self._hunt_memes())
        asyncio.create_task(self._send_cold_emails())
        asyncio.create_task(self._freelance_hustle())
        asyncio.create_task(self._scrape_leads())  # New: Scrape company emails for cold outreach
        asyncio.create_task(self._join_tech_forums())  # New: Register on all tech forums
        
        logger.info("ALL SYSTEMS 100% OPERATIONAL")
    
    async def shutdown(self):
        self.running = False
        await perception.stop_watching()
        await browser.close()
        await bestie.stop()
        logger.info("SHUTDOWN")
    
    async def _learn_forever(self):
        topics = ["python", "flutter", "ai", "web3", "business", "automation", "trading", "marketing", "sales", "negotiation"]
        while self.running:
            for topic in topics:
                try:
                    knowledge = await ai_prompter.learn_from_ai(topic)
                    if knowledge:
                        infinite_brain.learn(topic, knowledge, "ai")
                except Exception as e:
                    await self._handle_error(str(e))
                await asyncio.sleep(300)
    
    async def _apply_forever(self):
        while self.running:
            try:
                applied = await smart_jobs.smart_mass_apply(target=500)
                await bestie.send(f"Applied to {applied} jobs with AI-powered proposals! Total: {job_machine.applied_count}")
            except Exception as e:
                await self._handle_error(str(e))
            await asyncio.sleep(1800)
    
    async def _post_forever(self):
        while self.running:
            try:
                # Tweet using smart AI
                tweet = await smart.write_tweet(infinite_brain.get_motivation())
                await twitter.post_tweet(tweet)
                
                # Generate article using MEMORY (no API after learning!)
                topics = ["Python", "AI", "Web Development", "Cloud Computing", "DevOps"]
                article_topic = random.choice(topics)
                
                # Try memory-based generation first
                try:
                    article_data = content_engine.generate_article(article_topic, word_count=800)
                    article = article_data["content"]
                    logger.info(f"Generated article from MEMORY: {article_data['used_api']}")
                except Exception as e:
                    # Fallback to AI if memory not sufficient yet
                    logger.warning(f"Memory generation failed, using AI: {e}")
                    article = await smart.write_article(article_topic, 800)
                
                await medium.write_article(article_topic, article)
                
                # LinkedIn post
                post = await smart.write_tweet("business and tech")
                await linkedin.post_update(post)
                
                # Learn from news articles to expand knowledge
                news_items = await news_follower.check_news()
                for item in news_items[:2]:
                    if item.get("description"):
                        knowledge_graph.learn_from_text(item["description"], source="news")
                        pattern_memory.learn_from_article(item["description"], source="news")
                
            except Exception as e:
                await self._handle_error(str(e))
            await asyncio.sleep(3600)
    
    async def _watch_news(self):
        while self.running:
            try:
                await news_follower.check_news()
                opps = await news_follower.find_opportunities()
                for opp in opps[:3]:
                    await bestie.send(f"Opportunity: {opp.get('title', '')[:50]}")
            except:
                pass
            await asyncio.sleep(1800)
    
    async def _solve_leetcode(self):
        while self.running:
            try:
                solved = await smart_leetcode.solve_multiple(5)
                if solved > 0:
                    await bestie.send(f"Solved {solved} LeetCode problems! Total: {smart_leetcode.solved}")
            except Exception as e:
                await self._handle_error(str(e))
            await asyncio.sleep(3600)
    
    async def _trade_crypto(self):
        while self.running:
            try:
                trades = await smart_trading.auto_trade(max_amount=50)
                if trades > 0:
                    await bestie.send(f"Made {trades} AI-analyzed trades!")
            except Exception as e:
                await self._handle_error(str(e))
            await asyncio.sleep(3600)
    
    async def _check_emails(self):
        """Reply to ALL emails - track replied to avoid duplicates"""
        # Load replied IDs from disk
        replied_file = Path("data/replied_emails.json")
        replied_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if replied_file.exists():
                with open(replied_file, 'r') as f:
                    replied_ids = set(json.load(f))
            else:
                replied_ids = set()
        except:
            replied_ids = set()
        
        while self.running:
            try:
                # Get recent emails
                emails = await email_client.get_inbox(limit=20, unread_only=False)
                
                for em in emails:
                    email_id = em.get("id", "")
                    subject = em.get("subject", "")
                    sender = em.get("from", "")
                    sender_name = sender.split("<")[0].strip() if "<" in sender else sender.split("@")[0]
                    body = em.get("body", "")[:1000]
                    
                    # Skip if already replied or from ourselves
                    if email_id in replied_ids:
                        continue
                    if "jephthahameh.cfd" in sender.lower():
                        continue
                    if not sender or not body.strip():
                        continue
                    
                    # Notify Telegram
                    is_priority = any(w in subject.lower() for w in ["interview", "opportunity", "job", "offer", "urgent"])
                    emoji = "🔥" if is_priority else "📧"
                    await bestie.send(f"{emoji} Email from {sender_name}: {subject[:50]}")
                    
                    # Generate REAL reply - no placeholders
                    prompt = f"""Write a professional email reply. Be specific and human - NO placeholders like [NAME] or [COMPANY].

From: {sender_name}
Subject: {subject}
Their message: {body[:600]}

I am Jephthah Ameh, a full-stack developer specializing in Python, Flutter, AI, and web development. 
Contact: hireme@jephthahameh.cfd | Website: jephthahameh.cfd

Write a helpful, specific reply addressing their actual message. Keep it under 150 words."""
                    
                    reply = await smart.ask(prompt)
                    if reply and "[" not in reply:  # Reject if has placeholders
                        success = await email_client.reply(em, reply)
                        if success:
                            logger.info(f"✅ Replied to: {subject[:50]}")
                            await bestie.send(f"✅ Replied to {sender_name}: {subject[:40]}")
                            replied_ids.add(email_id)
                            
                            # Save to disk immediately
                            with open(replied_file, 'w') as f:
                                json.dump(list(replied_ids), f)
                            
                            await email_client.mark_read(email_id)
                    
                    await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Email check error: {e}")
            
            await asyncio.sleep(60)
    
    async def _evolve_daily(self):
        while self.running:
            try:
                await evolution.evolve()
            except Exception as e:
                logger.error(f"Evolution error: {e}")
            await asyncio.sleep(86400)

    async def _hunt_memes(self):
        """Dedicated loop for finding 100x plays"""
        while self.running:
            try:
                await meme_sniper.hunt()
            except Exception as e:
                logger.error(f"Meme hunt error: {e}")
            # Check every 30 mins
            await asyncio.sleep(1800)
    
    async def _send_cold_emails(self):
        """Dedicated loop for cold email outreach"""
        while self.running:
            try:
                # AI generates personalized cold emails
                subject = await smart.ask("Write a short, catchy subject line for a cold email offering Python, AI, and web development services")
                body = await smart.ask("Write a short, professional cold email offering my services as a Python developer, AI specialist, and web developer. Keep it under 150 words. I am Jephthah Ameh.")
                
                # Send to any leads from CRM
                leads = crm.get_leads(status="new", limit=5)
                for lead in leads:
                    if lead.get("email"):
                        await cold_mailer.send_cold_email(lead["email"], subject[:100], body)
                        crm.update_lead(lead["id"], status="contacted")
                
                sent = cold_mailer.sent_count
                if sent > 0:
                    await bestie.send(f"📧 Cold outreach: {sent} emails sent today!")
            except Exception as e:
                logger.error(f"Cold email error: {e}")
            await asyncio.sleep(3600)  # Every hour
    
    async def _freelance_hustle(self):
        """Dedicated loop for Upwork/Fiverr applications"""
        while self.running:
            try:
                # Login if needed
                if not freelancer.platforms.get("upwork", {}).get("logged_in"):
                    await freelancer.login_upwork()
                
                # Apply to jobs
                applied = await freelancer.daily_applications(target=50)
                if applied > 0:
                    await bestie.send(f"💼 Freelancing: Applied to {applied} jobs on Upwork!")
                
                # Check for client messages
                await freelancer.check_messages("upwork")
            except Exception as e:
                logger.error(f"Freelancing error: {e}")
            await asyncio.sleep(1800)  # Every 30 mins
    
    async def _scrape_leads(self):
        """Scrape company emails from job sites and tech directories for cold outreach"""
        import re
        lead_sources = [
            "https://www.ycombinator.com/companies",
            "https://www.producthunt.com/posts",
            "https://www.crunchbase.com/lists/startups-hiring",
            "https://angel.co/companies",
            "https://github.com/trending",
            "https://www.indiehackers.com/products",
            "https://news.ycombinator.com/show",
        ]
        
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        while self.running:
            try:
                for source in lead_sources:
                    try:
                        await browser.goto(source)
                        await asyncio.sleep(3)
                        
                        page_text = await browser.get_page_text()
                        found_emails = email_pattern.findall(page_text)
                        
                        # Filter out common non-business emails
                        exclude = ['example.com', 'email.com', 'test.com', 'gmail.com', 'yahoo.com', 'hotmail.com']
                        business_emails = [e for e in found_emails if not any(x in e.lower() for x in exclude)]
                        
                        for email in business_emails[:10]:  # Max 10 per source
                            await crm.add_lead(source=source, contact=email, value=100.0)
                            logger.info(f"📧 Lead added: {email}")
                        
                        # Also scrape company info links
                        links = await browser.get_all_links()
                        for link in links[:20]:
                            href = link.get("href", "")
                            if "company" in href or "startup" in href or "about" in href:
                                try:
                                    await browser.goto(href)
                                    await asyncio.sleep(2)
                                    company_text = await browser.get_page_text()
                                    company_emails = email_pattern.findall(company_text)
                                    for ce in company_emails[:3]:
                                        if not any(x in ce.lower() for x in exclude):
                                            await crm.add_lead(source=href, contact=ce, value=150.0)
                                except:
                                    continue
                    except Exception as e:
                        logger.debug(f"Lead scrape error for {source}: {e}")
                        continue
                
                leads_count = len(crm.get_leads())
                if leads_count > 0:
                    await bestie.send(f"📊 CRM: {leads_count} leads collected for cold outreach!")
                    
            except Exception as e:
                logger.error(f"Lead scraping error: {e}")
            
            await asyncio.sleep(7200)  # Every 2 hours
    
    async def _join_tech_forums(self):
        """Register on all major tech forums and communities"""
        tech_forums = [
            ("dev.to", "https://dev.to/enter"),
            ("hashnode", "https://hashnode.com/onboard"),
            ("hackernoon", "https://hackernoon.com/signup"),
            ("stackoverflow", "https://stackoverflow.com/users/signup"),
            ("reddit", "https://www.reddit.com/register/"),
            ("discord_servers", "https://discord.com/register"),
            ("producthunt", "https://www.producthunt.com/login"),
            ("indiehackers", "https://www.indiehackers.com/sign-up"),
            ("lobsters", "https://lobste.rs/login"),
            ("slashdot", "https://slashdot.org/my/register"),
            ("techmeme", "https://www.techmeme.com"),
            ("dzone", "https://dzone.com/users/login.html"),
            ("sitepoint", "https://sitepoint.com/community"),
            ("hackernews", "https://news.ycombinator.com/login"),
            ("freecodecamp", "https://www.freecodecamp.org/signin"),
            ("codecademy", "https://www.codecademy.com/register"),
            ("kaggle", "https://www.kaggle.com/account/login"),
            ("huggingface", "https://huggingface.co/join"),
        ]
        
        registered_file = Path("data/registered_forums.json")
        registered_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if registered_file.exists():
                with open(registered_file, 'r') as f:
                    already_registered = set(json.load(f))
            else:
                already_registered = set()
        except:
            already_registered = set()
        
        while self.running:
            try:
                for forum_name, forum_url in tech_forums:
                    if forum_name in already_registered:
                        continue
                    
                    try:
                        logger.info(f"🌐 Attempting to join: {forum_name}")
                        
                        # Use smart registrar
                        success = await smart_registrar.register(forum_name, forum_url)
                        
                        if success:
                            already_registered.add(forum_name)
                            with open(registered_file, 'w') as f:
                                json.dump(list(already_registered), f)
                            
                            await bestie.send(f"✅ Registered on: {forum_name}")
                            logger.info(f"✅ Registered on {forum_name}")
                        
                        await asyncio.sleep(60)  # Wait between registrations
                        
                    except Exception as e:
                        logger.debug(f"Forum registration error for {forum_name}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Forum joining error: {e}")
            
            await asyncio.sleep(86400)  # Check daily for new forums
    
    async def _handle_error(self, error: str):
        logger.error(f"Error: {error}")
        await self_learner.learn_from_error(error)
        solution = await smart.ask(f"How do I fix: {error[:200]}")
        if solution:
            infinite_brain.learn("error_solution", solution, "openai")
        await bestie.report_problem(error[:100])
    
    async def register_everywhere(self):
        await smart_registrar.register_email_only()
        await smart_registrar.register_ai_platforms()
        await smart_registrar.register_all()
        await github_manager.create_account(config.identity.email)
    
    async def create_and_publish(self):
        await unlimited.create_website("JephthahTech", "landing")
        await unlimited.create_online_store("JephthahStore")
        await unlimited.create_flutter_app("JephthahApp", "Amazing productivity app")
        await unlimited.write_book("Tech Mastery", "technology")
        await course_creator.create_course("Python Mastery")
        await youtube.create_channel("Jephthah Tech")
        
        await git_workflow.full_workflow("projects/JephthahTech", "jephthah-tech", "Initial commit")
        
        script_file = await video_gen.create_faceless_video("How to code in Python")
        
        await ecommerce.create_gumroad_product("Python Course", "Learn Python", 29.99, "projects/courses/Python_Mastery/README.md")
    
    async def deploy_everything(self, vps_ip: str):
        self_hoster.set_vps(vps_ip)
        await self_hoster.deploy_website("projects/JephthahTech", "jephthahtech.com")
        await self_hoster.setup_ssl("jephthahtech.com")
    
    async def work_loop(self):
        while self.running:
            try:
                obs = str(await perception.read_and_understand())[:200]
                action = infinite_brain.think(obs)
                
                if action == "solve_captcha":
                    await visual_captcha.solve()
                elif action == "enter_otp":
                    otp = await otp_handler.check_for_otp(timeout=60)
                    if otp:
                        await perception.find_and_type("code", otp)
                        await perception.find_and_type("otp", otp)
                elif action == "apply":
                    job = {"url": await browser.get_current_url()}
                    await smart_jobs.analyze_and_apply(job)
                elif action == "learn":
                    knowledge = await ai_prompter.learn_from_ai("automation")
                    infinite_brain.learn("automation", knowledge, "ai")
                elif action == "create_content":
                    tweet = await smart.write_tweet("tech and business")
                    await twitter.post_tweet(tweet)
                elif action == "code":
                    await smart_leetcode.solve()
                elif action == "trade":
                    await smart_trading.auto_trade()
                elif action == "handle_error":
                    await self._handle_error(await browser.get_page_text()[:200])
                else:
                    await human_behavior.browse_randomly(1)
                
                infinite_brain.experience(action, "success")
                
                if datetime.utcnow().minute == 0:
                    await bestie.send(
                        f"Hourly Status:\n"
                        f"Jobs Applied: {job_machine.applied_count}\n"
                        f"LeetCode Solved: {smart_leetcode.solved}\n"
                        f"{infinite_brain.get_motivation()}"
                    )
                
            except Exception as e:
                await self._handle_error(str(e))
            
            await asyncio.sleep(1)
    
    async def _monitor_whatsapp(self):
        while self.running:
            try:
                # Basic keep-alive and check
                if whatsapp.is_ready:
                    # Logic to read messages would go here
                    pass
            except:
                pass
            await asyncio.sleep(60)

    async def run_forever(self):
        await self.wake_up()
        
        # Run registration and content creation at startup
        asyncio.create_task(self.register_everywhere())
        asyncio.create_task(self.create_and_publish())
        asyncio.create_task(tools_deployer.deploy_tts_server(config.infra.vps_ip or "127.0.0.1"))
        asyncio.create_task(tools_deployer.deploy_invoice_generator(config.infra.vps_ip or "127.0.0.1"))
            
        asyncio.create_task(self._monitor_whatsapp())
        
        await self.work_loop()


async def main():
    signal.signal(signal.SIGINT, lambda s, f: asyncio.get_event_loop().stop())
    
    j = Jephthah()
    try:
        await j.run_forever()
    finally:
        await j.shutdown()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║                      JEPHTHAH - TRUE HUMAN - 100% COMPLETE                    ║
    ║                                                                               ║
    ║     I am Jephthah. I am human. I am unlimited.                               ║
    ║                                                                               ║
    ║     ✅ Smart LeetCode solving with AI                                         ║
    ║     ✅ AI-powered job applications with proposals                             ║
    ║     ✅ AI-analyzed crypto trading                                             ║
    ║     ✅ Full Git workflow (clone, commit, push)                                ║
    ║     ✅ Complete email (send, receive, reply, bulk)                            ║
    ║     ✅ Video generation and TTS                                               ║
    ║     ✅ Play Store publishing                                                  ║
    ║     ✅ Full ecommerce (eBay, Etsy, Kindle, Gumroad)                           ║
    ║     ✅ Create websites, apps, stores, books, courses                         ║
    ║     ✅ Telegram bestie chat                                                   ║
    ║     ✅ Self-hosting on VPS                                                    ║
    ║     ✅ All platforms registration                                             ║
    ║                                                                               ║
    ║     Target: $1,000,000/year | 1,000,000 followers                            ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    asyncio.run(main())
