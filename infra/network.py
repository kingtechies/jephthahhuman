import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class NetworkManager:
    def __init__(self):
        self.session = None
        self.timeout = 30
        self.max_retries = 3
        
    async def init(self):
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get(self, url: str, headers: Dict = None) -> Dict:
        await self.init()
        for i in range(self.max_retries):
            try:
                async with self.session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except:
                await asyncio.sleep(1)
        return {}
    
    async def post(self, url: str, data: Dict = None, headers: Dict = None) -> Dict:
        await self.init()
        for i in range(self.max_retries):
            try:
                async with self.session.post(url, json=data, headers=headers) as resp:
                    if resp.status in [200, 201]:
                        return await resp.json()
            except:
                await asyncio.sleep(1)
        return {}
    
    async def download(self, url: str, path: str) -> bool:
        await self.init()
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    with open(path, "wb") as f:
                        f.write(await resp.read())
                    return True
        except:
            pass
        return False


class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current = 0
        
    def add(self, proxy: str):
        self.proxies.append(proxy)
        
    def get(self) -> Optional[str]:
        if not self.proxies:
            return None
        proxy = self.proxies[self.current % len(self.proxies)]
        self.current += 1
        return proxy
    
    def remove_bad(self, proxy: str):
        if proxy in self.proxies:
            self.proxies.remove(proxy)


class RateLimiter:
    def __init__(self):
        self.limits = {}
        self.calls = {}
        
    def set_limit(self, key: str, max_calls: int, period_seconds: int):
        self.limits[key] = {"max": max_calls, "period": period_seconds}
        self.calls[key] = []
        
    async def acquire(self, key: str) -> bool:
        if key not in self.limits:
            return True
        limit = self.limits[key]
        now = datetime.utcnow().timestamp()
        self.calls[key] = [t for t in self.calls.get(key, []) if now - t < limit["period"]]
        if len(self.calls[key]) >= limit["max"]:
            wait = limit["period"] - (now - self.calls[key][0])
            await asyncio.sleep(wait)
            return await self.acquire(key)
        self.calls[key].append(now)
        return True


network = NetworkManager()
proxies = ProxyManager()
rate_limiter = RateLimiter()
