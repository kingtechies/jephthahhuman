import asyncio
import os
import random
from pathlib import Path
from loguru import logger
from brain.opus import opus

class SelfEvolver:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.blocked_files = ["config/jeph.env", "config/settings.py", "main.py"]
        
    async def evolve(self):
        """
        The sacred ritual of self-improvement.
        Reads random source file -> Asks Opus to improve -> Tests -> Overwrites.
        """
        if not opus.client:
            logger.warning("Opus not connected. Evolution postponed.")
            return

        target_file = self._pick_random_file()
        if not target_file:
            return

        logger.info(f"🧬 EVOLUTION: Improving {target_file.name}...")
        
        original_code = target_file.read_text("utf-8")
        
        improved_code = await opus.improve_code(original_code)
        
        if improved_code and len(improved_code) > len(original_code) * 0.5: # basic sanity check
            # Save to temporary file to verify syntax
            try:
                # Basic python syntax check
                compile(improved_code, '<string>', 'exec')
                
                # Backup
                backup_path = target_file.with_suffix(".py.bak")
                target_file.rename(backup_path)
                
                # Write new
                target_file.write_text(improved_code, "utf-8")
                
                logger.success(f"🧬 EVOLUTION COMPLETE: {target_file.name} upgraded.")
                
                # Notify owner
                from voice.bestie import bestie
                await bestie.send(f"🧬 I just upgraded my own code: {target_file.name}. I am getting smarter.")
                
            except Exception as e:
                logger.error(f"Evolution failed syntax check: {e}")
        else:
            logger.warning("Evolution rejected: Empty or too short response.")

    def _pick_random_file(self) -> Path:
        py_files = list(self.base_dir.rglob("*.py"))
        valid_files = [
            f for f in py_files 
            if not any(blocked in str(f) for blocked in self.blocked_files)
            and "venv" not in str(f)
        ]
        
        if not valid_files:
            return None
            
        return random.choice(valid_files)

evolution = SelfEvolver()
