"""
Jephthah File System Manager
File and Git operations
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import subprocess

from loguru import logger

from config.settings import config, BASE_DIR


class FileManager:
    """File system operations"""
    
    def __init__(self):
        self.workspace = BASE_DIR / "workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"File manager initialized: {self.workspace}")
    
    def create_file(self, path: str, content: str = "") -> bool:
        """Create a file with content"""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            logger.info(f"Created file: {path}")
            return True
        except Exception as e:
            logger.error(f"Create file error: {e}")
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        try:
            return Path(path).read_text()
        except Exception as e:
            logger.error(f"Read file error: {e}")
            return None
    
    def append_file(self, path: str, content: str) -> bool:
        """Append to file"""
        try:
            with open(path, 'a') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Append file error: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """Delete a file"""
        try:
            Path(path).unlink()
            logger.info(f"Deleted file: {path}")
            return True
        except Exception as e:
            logger.error(f"Delete file error: {e}")
            return False
    
    def create_folder(self, path: str) -> bool:
        """Create a folder"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {path}")
            return True
        except Exception as e:
            logger.error(f"Create folder error: {e}")
            return False
    
    def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """List files in a directory"""
        try:
            return [str(f) for f in Path(path).glob(pattern)]
        except Exception as e:
            logger.error(f"List files error: {e}")
            return []
    
    def copy_file(self, source: str, dest: str) -> bool:
        """Copy a file"""
        try:
            shutil.copy2(source, dest)
            return True
        except Exception as e:
            logger.error(f"Copy file error: {e}")
            return False
    
    def move_file(self, source: str, dest: str) -> bool:
        """Move a file"""
        try:
            shutil.move(source, dest)
            return True
        except Exception as e:
            logger.error(f"Move file error: {e}")
            return False


class GitManager:
    """Git operations"""
    
    def __init__(self):
        self.github_token = config.infra.github_token
        self.github_username = config.infra.github_username
        
        logger.info("Git manager initialized")
    
    def _run_git(self, args: List[str], cwd: str = None) -> tuple:
        """Run a git command"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def clone(self, repo_url: str, target_dir: str = None) -> bool:
        """Clone a repository"""
        # Add token for private repos
        if self.github_token and "github.com" in repo_url:
            repo_url = repo_url.replace(
                "https://github.com",
                f"https://{self.github_token}@github.com"
            )
        
        success, stdout, stderr = self._run_git(["clone", repo_url, target_dir] if target_dir else ["clone", repo_url])
        
        if success:
            logger.info(f"Cloned: {repo_url}")
        else:
            logger.error(f"Clone failed: {stderr}")
        
        return success
    
    def init(self, path: str) -> bool:
        """Initialize a new repository"""
        success, _, _ = self._run_git(["init"], cwd=path)
        return success
    
    def add(self, path: str, files: str = ".") -> bool:
        """Add files to staging"""
        success, _, _ = self._run_git(["add", files], cwd=path)
        return success
    
    def commit(self, path: str, message: str) -> bool:
        """Commit changes"""
        success, _, stderr = self._run_git(["commit", "-m", message], cwd=path)
        if success:
            logger.info(f"Committed: {message}")
        return success
    
    def push(self, path: str, remote: str = "origin", branch: str = "main") -> bool:
        """Push to remote"""
        success, _, stderr = self._run_git(["push", remote, branch], cwd=path)
        if success:
            logger.info(f"Pushed to {remote}/{branch}")
        else:
            logger.error(f"Push failed: {stderr}")
        return success
    
    def pull(self, path: str, remote: str = "origin", branch: str = "main") -> bool:
        """Pull from remote"""
        success, _, _ = self._run_git(["pull", remote, branch], cwd=path)
        return success
    
    def status(self, path: str) -> str:
        """Get repository status"""
        success, stdout, _ = self._run_git(["status", "--short"], cwd=path)
        return stdout if success else ""
    
    def create_branch(self, path: str, branch_name: str) -> bool:
        """Create a new branch"""
        success, _, _ = self._run_git(["checkout", "-b", branch_name], cwd=path)
        return success
    
    def checkout(self, path: str, branch: str) -> bool:
        """Checkout a branch"""
        success, _, _ = self._run_git(["checkout", branch], cwd=path)
        return success
    
    def create_repo(self, name: str, private: bool = False) -> Optional[str]:
        """Create a new GitHub repository"""
        if not self.github_token:
            logger.warning("No GitHub token configured")
            return None
        
        try:
            import httpx
            
            response = httpx.post(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "name": name,
                    "private": private,
                    "auto_init": True
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"Created repo: {data['html_url']}")
                return data["clone_url"]
            else:
                logger.error(f"Create repo failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Create repo error: {e}")
            return None


# Global instances
files = FileManager()
git = GitManager()
