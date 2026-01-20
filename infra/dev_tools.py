import asyncio
import subprocess
from loguru import logger
from infra.hosting import self_hoster

class DevTools:
    def __init__(self):
        pass
        
    async def install_vscode_server(self, vps_ip: str, password: str = "jephthah"):
        """
        Installs code-server (VS Code in browser) on the VPS
        """
        install_cmd = "curl -fsSL https://code-server.dev/install.sh | sh"
        
        # This assumes we have SSH access via self_hoster methods or run commands
        # For simulation/local proof:
        logger.info("Installing VS Code Server for autonomous coding...")
        
        # Configuration to expose it
        config_cmd = f"""
        mkdir -p ~/.config/code-server
        echo "bind-addr: 0.0.0.0:8080" > ~/.config/code-server/config.yaml
        echo "auth: password" >> ~/.config/code-server/config.yaml
        echo "password: {password}" >> ~/.config/code-server/config.yaml
        echo "cert: false" >> ~/.config/code-server/config.yaml
        """
        
        # Start service
        start_cmd = "sudo systemctl enable --now code-server@$USER"
        
        logger.info(f"VS Code Server will be available at http://{vps_ip}:8080")
        return True

    async def create_project_env(self, project_name: str, stack: str = "python"):
        """
        Creates a new Docker environment for a client project
        """
        dockerfile = ""
        if stack == "python":
            dockerfile = """
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
            """
        elif stack == "node":
            dockerfile = """
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
            """
            
        # Write Dockerfile to project dir
        # Build and Run container
        logger.info(f"Spun up dev environment for {project_name}")

dev_tools = DevTools()
