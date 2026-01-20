import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from config.settings import BASE_DIR


class SelfHoster:
    def __init__(self):
        self.hosted_apps = []
        self.vps_ip = None
        self.ssh_user = "root"
        
    def set_vps(self, ip: str, user: str = "root"):
        self.vps_ip = ip
        self.ssh_user = user
    
    async def deploy_website(self, project_path: str, domain: str) -> bool:
        if not self.vps_ip:
            logger.warning("VPS not configured")
            return False
        
        try:
            cmd = f"rsync -avz {project_path}/ {self.ssh_user}@{self.vps_ip}:/var/www/{domain}/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            nginx_config = f"""
server {{
    listen 80;
    server_name {domain};
    root /var/www/{domain};
    index index.html;
    location / {{
        try_files $uri $uri/ =404;
    }}
}}
"""
            config_cmd = f'echo \'{nginx_config}\' | ssh {self.ssh_user}@{self.vps_ip} "cat > /etc/nginx/sites-available/{domain}"'
            subprocess.run(config_cmd, shell=True)
            
            enable_cmd = f'ssh {self.ssh_user}@{self.vps_ip} "ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/ && nginx -t && systemctl reload nginx"'
            subprocess.run(enable_cmd, shell=True)
            
            self.hosted_apps.append({"type": "website", "domain": domain, "path": project_path})
            logger.info(f"Deployed website: {domain}")
            return True
        except Exception as e:
            logger.error(f"Deploy error: {e}")
            return False
    
    async def deploy_python_app(self, project_path: str, port: int, name: str) -> bool:
        if not self.vps_ip:
            return False
        
        try:
            cmd = f"rsync -avz {project_path}/ {self.ssh_user}@{self.vps_ip}:/opt/{name}/"
            subprocess.run(cmd, shell=True)
            
            service = f"""
[Unit]
Description={name}
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/{name}
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
            service_cmd = f'echo \'{service}\' | ssh {self.ssh_user}@{self.vps_ip} "cat > /etc/systemd/system/{name}.service"'
            subprocess.run(service_cmd, shell=True)
            
            start_cmd = f'ssh {self.ssh_user}@{self.vps_ip} "systemctl daemon-reload && systemctl enable {name} && systemctl start {name}"'
            subprocess.run(start_cmd, shell=True)
            
            self.hosted_apps.append({"type": "python", "name": name, "port": port})
            logger.info(f"Deployed Python app: {name}")
            return True
        except Exception as e:
            logger.error(f"Deploy error: {e}")
            return False
    
    async def deploy_docker(self, image: str, port: int, name: str) -> bool:
        if not self.vps_ip:
            return False
        
        try:
            cmd = f'ssh {self.ssh_user}@{self.vps_ip} "docker run -d --name {name} -p {port}:{port} {image}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            self.hosted_apps.append({"type": "docker", "image": image, "name": name, "port": port})
            logger.info(f"Deployed Docker: {name}")
            return True
        except:
            return False
    
    async def install_software(self, software: str) -> bool:
        if not self.vps_ip:
            return False
        
        try:
            cmd = f'ssh {self.ssh_user}@{self.vps_ip} "apt-get update && apt-get install -y {software}"'
            subprocess.run(cmd, shell=True)
            return True
        except:
            return False
    
    async def run_command(self, command: str) -> str:
        if not self.vps_ip:
            return ""
        
        try:
            cmd = f'ssh {self.ssh_user}@{self.vps_ip} "{command}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    async def setup_database(self, db_type: str = "sqlite") -> bool:
        if db_type == "sqlite":
            return True
        elif db_type == "postgres":
            return await self.install_software("postgresql")
        elif db_type == "mysql":
            return await self.install_software("mysql-server")
        return False
    
    async def setup_ssl(self, domain: str) -> bool:
        if not self.vps_ip:
            return False
        
        try:
            cmd = f'ssh {self.ssh_user}@{self.vps_ip} "certbot --nginx -d {domain} --non-interactive --agree-tos -m hireme@jephthahameh.cfd"'
            subprocess.run(cmd, shell=True)
            return True
        except:
            return False
    
    def get_hosted_apps(self) -> List[Dict]:
        return self.hosted_apps


class PlatformPreference:
    def __init__(self):
        self.phone_required = {
            "twitter": True,
            "facebook": True,
            "instagram": True,
            "tiktok": True,
            "whatsapp": True,
            "telegram": True,
        }
        
        self.email_only = {
            "medium": True,
            "dev.to": True,
            "hashnode": True,
            "github": True,
            "upwork": True,
            "fiverr": True,
            "linkedin": False,
            "reddit": True,
            "substack": True,
            "gumroad": True,
            "producthunt": True,
        }
        
        self.priority_platforms = [
            "github",
            "linkedin",
            "medium",
            "dev.to",
            "upwork",
            "fiverr",
            "reddit",
            "hashnode",
            "producthunt",
            "gumroad",
        ]
    
    def needs_phone(self, platform: str) -> bool:
        return self.phone_required.get(platform.lower(), False)
    
    def is_email_only(self, platform: str) -> bool:
        return self.email_only.get(platform.lower(), True)
    
    def get_priority_platforms(self) -> List[str]:
        return self.priority_platforms
    
    def should_skip(self, platform: str) -> bool:
        return self.needs_phone(platform)


self_hoster = SelfHoster()
platform_pref = PlatformPreference()
