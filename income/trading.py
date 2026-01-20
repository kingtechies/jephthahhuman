import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

try:
    import ccxt
    HAS_CCXT = True
except:
    HAS_CCXT = False

from config.settings import config
from brain.memory import memory


class CryptoTrader:
    def __init__(self):
        self.exchanges = {}
        self.portfolio = {}
        self.alerts = []
        self.trades_today = 0
        
    async def init_exchange(self, name: str = "binance"):
        if not HAS_CCXT:
            return False
        try:
            api_key = getattr(config.crypto, f"{name}_api_key", None)
            api_secret = getattr(config.crypto, f"{name}_api_secret", None)
            if not api_key or not api_secret:
                return False
            exchange_class = getattr(ccxt, name)
            self.exchanges[name] = exchange_class({
                "apiKey": api_key,
                "secret": api_secret,
                "enableRateLimit": True
            })
            return True
        except:
            return False
    
    async def get_price(self, symbol: str, exchange: str = "binance") -> float:
        if exchange not in self.exchanges:
            return 0.0
        try:
            ticker = self.exchanges[exchange].fetch_ticker(symbol)
            return ticker.get("last", 0.0)
        except:
            return 0.0
    
    async def get_balance(self, exchange: str = "binance") -> Dict:
        if exchange not in self.exchanges:
            return {}
        try:
            balance = self.exchanges[exchange].fetch_balance()
            return {k: v for k, v in balance["total"].items() if v > 0}
        except:
            return {}
    
    async def buy(self, symbol: str, amount: float, exchange: str = "binance") -> bool:
        if exchange not in self.exchanges:
            return False
        try:
            order = self.exchanges[exchange].create_market_buy_order(symbol, amount)
            self.trades_today += 1
            memory.log_action("trading", "buy", exchange, "success", {
                "symbol": symbol, "amount": amount, "order": order["id"]
            })
            return True
        except Exception as e:
            logger.error(f"Buy error: {e}")
            return False
    
    async def sell(self, symbol: str, amount: float, exchange: str = "binance") -> bool:
        if exchange not in self.exchanges:
            return False
        try:
            order = self.exchanges[exchange].create_market_sell_order(symbol, amount)
            self.trades_today += 1
            memory.log_action("trading", "sell", exchange, "success", {
                "symbol": symbol, "amount": amount, "order": order["id"]
            })
            return True
        except Exception as e:
            logger.error(f"Sell error: {e}")
            return False
    
    async def monitor_prices(self, symbols: List[str] = None, callback = None):
        symbols = symbols or ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        while True:
            for symbol in symbols:
                price = await self.get_price(symbol)
                if callback:
                    await callback(symbol, price)
            await asyncio.sleep(60)
    
    def add_alert(self, symbol: str, condition: str, target: float):
        self.alerts.append({
            "symbol": symbol,
            "condition": condition,
            "target": target,
            "created": datetime.utcnow().isoformat()
        })


class DeFiFarmer:
    def __init__(self):
        self.protocols = []
        self.positions = []
        
    async def find_yields(self) -> List[Dict]:
        from hands.browser import browser
        try:
            await browser.goto("https://defillama.com/yields")
            await asyncio.sleep(3)
            text = await browser.get_page_text()
            return []
        except:
            return []
    
    async def farm(self, protocol: str):
        pass


class AirdropHunter:
    def __init__(self):
        self.claimed = []
        self.pending = []
        
    async def check_eligibility(self, address: str) -> List[Dict]:
        from hands.browser import browser
        sites = [
            "https://earni.fi/",
            "https://airdrops.io/",
        ]
        eligible = []
        for site in sites:
            try:
                await browser.goto(site)
                await asyncio.sleep(2)
            except:
                pass
        return eligible
    
    async def claim(self, airdrop: Dict) -> bool:
        return False


crypto_trader = CryptoTrader()
defi_farmer = DeFiFarmer()
airdrop_hunter = AirdropHunter()
