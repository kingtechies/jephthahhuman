import asyncio
import subprocess
from pathlib import Path
from loguru import logger
from infra.hosting import self_hoster

class SelfHostTools:
    def __init__(self):
        self.tools_dir = Path("projects/tools")
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    async def deploy_tts_server(self, vps_ip: str):
        # Create a simple Flask TTS server using pyttsx3 or gTTS
        server_code = """
from flask import Flask, request, send_file
import gtts
import os
import uuid

app = Flask(__name__)

@app.route('/speak', methods=['GET'])
def speak():
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'en')
    if not text:
        return "No text provided", 400
    
    filename = f"{uuid.uuid4()}.mp3"
    tts = gtts.gTTS(text, lang=lang)
    tts.save(filename)
    
    return send_file(filename, mimetype='audio/mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""
        app_dir = self.tools_dir / "tts_server"
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "main.py").write_text(server_code)
        (app_dir / "requirements.txt").write_text("flask\ngTTS\n")
        
        await self_hoster.set_vps(vps_ip)
        success = await self_hoster.deploy_python_app(str(app_dir), 5000, "tts-server")
        if success:
            logger.info(f"Self-hosted TTS deployed at http://{vps_ip}:5000")
            
    async def deploy_invoice_generator(self, vps_ip: str):
        # Deploy a simple React/HTML invoice generator
        # Cloning a popular open source one or creating a simple one
        # For simplicity, we create a basic one
        
        html_content = """
<!DOCTYPE html>
<html>
<head><title>Jephthah Invoices</title></head>
<body>
    <h1>Invoice Generator</h1>
    <form id="invForm">
        <input type="text" placeholder="Client Name" id="client">
        <input type="number" placeholder="Amount" id="amount">
        <button onclick="generate()">Generate</button>
    </form>
    <div id="preview"></div>
    <script>
        function generate() {
            const client = document.getElementById('client').value;
            const amount = document.getElementById('amount').value;
            document.getElementById('preview').innerHTML = `<h2>Invoice for ${client}</h2><p>Total: $${amount}</p>`;
        }
    </script>
</body>
</html>
"""
        app_dir = self.tools_dir / "invoice_gen"
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "index.html").write_text(html_content)
        
        await self_hoster.deploy_website(str(app_dir), "invoices.jephthahameh.cfd")

tools_deployer = SelfHostTools()
