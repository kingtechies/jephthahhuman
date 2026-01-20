import asyncio
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config


class GitWorkflow:
    def __init__(self):
        self.current_repo = None
        self.username = config.github_username or "jephthah"
        self.token = config.github_token
        
    async def clone(self, repo_url: str, target_dir: str = None) -> bool:
        target = target_dir or repo_url.split("/")[-1].replace(".git", "")
        cmd = f"git clone {repo_url} {target}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            self.current_repo = target
            logger.info(f"Cloned: {repo_url}")
            return True
        return False
    
    async def init(self, directory: str) -> bool:
        cmd = f"cd {directory} && git init"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            self.current_repo = directory
            return True
        return False
    
    async def add(self, files: str = ".") -> bool:
        cmd = f"cd {self.current_repo} && git add {files}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    async def commit(self, message: str) -> bool:
        cmd = f'cd {self.current_repo} && git commit -m "{message}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.info(f"Commit: {message}")
        return result.returncode == 0
    
    async def push(self, remote: str = "origin", branch: str = "main") -> bool:
        if self.token:
            cmd = f"cd {self.current_repo} && git push https://{self.token}@github.com/{self.username}/{os.path.basename(self.current_repo)}.git {branch}"
        else:
            cmd = f"cd {self.current_repo} && git push {remote} {branch}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Pushed to {remote}/{branch}")
            return True
        return False
    
    async def pull(self, remote: str = "origin", branch: str = "main") -> bool:
        cmd = f"cd {self.current_repo} && git pull {remote} {branch}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    async def create_branch(self, name: str) -> bool:
        cmd = f"cd {self.current_repo} && git checkout -b {name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    async def checkout(self, branch: str) -> bool:
        cmd = f"cd {self.current_repo} && git checkout {branch}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    async def status(self) -> str:
        cmd = f"cd {self.current_repo} && git status"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    async def log(self, count: int = 5) -> str:
        cmd = f"cd {self.current_repo} && git log -n {count} --oneline"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    async def create_github_repo(self, name: str, private: bool = False) -> bool:
        if not self.token:
            return False
        
        import aiohttp
        headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"}
        data = {"name": name, "private": private, "auto_init": True}
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.github.com/user/repos", headers=headers, json=data) as resp:
                if resp.status == 201:
                    logger.info(f"GitHub repo created: {name}")
                    return True
        return False
    
    async def full_workflow(self, directory: str, repo_name: str, commit_msg: str = "Update") -> bool:
        await self.init(directory)
        await self.add()
        await self.commit(commit_msg)
        await self.create_github_repo(repo_name)
        
        remote_url = f"https://github.com/{self.username}/{repo_name}.git"
        subprocess.run(f"cd {directory} && git remote add origin {remote_url}", shell=True)
        
        return await self.push()


git_workflow = GitWorkflow()
