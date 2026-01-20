import asyncio
import random
from datetime import datetime
from typing import Dict, List
from loguru import logger

from config.settings import config
from hands.browser import browser
from eyes.perception import perception
from brain.smart import smart


class SmartLeetCode:
    def __init__(self):
        self.solved = 0
        self.solutions = {}
        
    async def solve(self, problem_url: str = None) -> bool:
        if problem_url:
            await browser.goto(problem_url)
        else:
            await browser.goto("https://leetcode.com/problemset/all/")
            await asyncio.sleep(2)
            
            links = await browser.get_all_links()
            for link in links:
                href = link.get("href", "")
                if "/problems/" in href and "problemset" not in href:
                    await browser.goto(href)
                    break
        
        await asyncio.sleep(3)
        
        problem_text = await browser.get_page_text()
        
        title_element = await browser.page.query_selector('[data-cy="question-title"]')
        title = await title_element.inner_text() if title_element else "unknown"
        
        solution = await smart.solve_leetcode(problem_text[:3000])
        
        if not solution:
            return False
        
        lang_selector = await browser.page.query_selector('[data-cy="lang-select"]')
        if lang_selector:
            await lang_selector.click()
            await asyncio.sleep(1)
            await perception.find_and_click("Python3")
            await asyncio.sleep(1)
        
        editor = await browser.page.query_selector('.monaco-editor textarea, [data-mode-id="python"]')
        if editor:
            await browser.page.keyboard.press("Control+a")
            await asyncio.sleep(0.2)
            await browser.page.keyboard.type(solution)
            await asyncio.sleep(1)
        
        await perception.find_and_click("Submit")
        await asyncio.sleep(10)
        
        result_text = await browser.get_page_text()
        
        if "accepted" in result_text.lower():
            self.solved += 1
            self.solutions[title] = solution
            logger.info(f"LeetCode SOLVED: {title}")
            
            from voice.bestie import bestie
            await bestie.share_win(f"Solved LeetCode: {title}!")
            return True
        else:
            logger.info(f"LeetCode failed: {title}")
            return False
    
    async def solve_multiple(self, count: int = 10) -> int:
        solved = 0
        await browser.goto("https://leetcode.com/problemset/all/?difficulty=EASY")
        await asyncio.sleep(2)
        
        links = await browser.get_all_links()
        problem_links = [l for l in links if "/problems/" in l.get("href", "") and "problemset" not in l.get("href", "")]
        
        for link in problem_links[:count]:
            if await self.solve(link["href"]):
                solved += 1
            await asyncio.sleep(5)
        
        return solved


class SmartTrading:
    def __init__(self):
        self.trades = []
        self.pnl = 0.0
        
    async def analyze_market(self, symbol: str = "BTC") -> Dict:
        analysis = await smart.ask(f"Give brief crypto analysis for {symbol}. Should I buy, sell, or hold? Why?")
        
        decision = "hold"
        if "buy" in analysis.lower():
            decision = "buy"
        elif "sell" in analysis.lower():
            decision = "sell"
        
        return {
            "symbol": symbol,
            "analysis": analysis,
            "decision": decision,
            "confidence": 0.7
        }
    
    async def execute_trade(self, symbol: str, action: str, amount: float) -> bool:
        from income.trading import crypto_trader
        
        if action == "buy":
            success = await crypto_trader.buy(f"{symbol}/USDT", amount)
        else:
            success = await crypto_trader.sell(f"{symbol}/USDT", amount)
        
        if success:
            self.trades.append({
                "symbol": symbol,
                "action": action,
                "amount": amount,
                "time": datetime.utcnow().isoformat()
            })
            
            from voice.bestie import bestie
            await bestie.send(f"Trade executed: {action.upper()} {amount} {symbol}")
        
        return success
    
    async def auto_trade(self, symbols: List[str] = None, max_amount: float = 100) -> int:
        symbols = symbols or ["BTC", "ETH", "SOL"]
        trades = 0
        
        for symbol in symbols:
            analysis = await self.analyze_market(symbol)
            
            if analysis["decision"] != "hold" and analysis["confidence"] > 0.6:
                amount = max_amount * analysis["confidence"]
                if await self.execute_trade(symbol, analysis["decision"], amount):
                    trades += 1
            
            await asyncio.sleep(60)
        
        return trades


class SmartJobApply:
    def __init__(self):
        self.applied = 0
        
    async def analyze_and_apply(self, job: Dict) -> bool:
        job_text = f"Title: {job.get('title', '')}\nDescription: {job.get('description', '')}"
        
        analysis = await smart.analyze_job(job_text[:2000])
        
        if not analysis.get("apply", True):
            return False
        
        proposal = await smart.write_proposal(job_text[:1000])
        
        from income.job_machine import job_machine
        job["proposal"] = proposal
        
        success = await job_machine.apply_single(job)
        
        if success:
            self.applied += 1
            
            if analysis.get("skills_match", 0) > 80:
                from voice.bestie import bestie
                await bestie.send(f"Applied to high-match job: {job.get('title', '')[:50]}")
        
        return success
    
    async def smart_mass_apply(self, target: int = 100) -> int:
        from income.job_machine import job_machine
        
        applied = 0
        for skill in job_machine.skills[:5]:
            jobs = await job_machine.hunt_jobs(skill)
            
            for job in jobs:
                if applied >= target:
                    break
                
                if await self.analyze_and_apply(job):
                    applied += 1
                
                await asyncio.sleep(10)
            
            if applied >= target:
                break
        
        return applied


smart_leetcode = SmartLeetCode()
smart_trading = SmartTrading()
smart_jobs = SmartJobApply()
