import asyncio
import re
import email
import imaplib
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from loguru import logger

from config.settings import config


class EmailOTPChecker:
    def __init__(self):
        self.email = config.identity.email
        self.password = config.identity.email_password
        self.imap_server = "mail.jephthahameh.cfd"
        self.imap_port = 993
        
        self.otp_patterns = [
            re.compile(r'(?:code|OTP|pin|token|verification)[:\s]+(\d{4,8})', re.I),
            re.compile(r'(\d{4,8})\s+(?:is your|verification)', re.I),
            re.compile(r'enter[:\s]+(\d{4,8})', re.I),
            re.compile(r'(?:code|otp)[:\s]*(\d{6})', re.I),
            re.compile(r'\b(\d{6})\b'),
        ]
        
    async def check_for_otp(self, from_filter: str = None, timeout: int = 120) -> Optional[str]:
        if not self.password:
            logger.warning("Email password not set")
            return None
        
        logger.info(f"Checking email for OTP (timeout: {timeout}s)")
        
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).seconds < timeout:
            try:
                otp = await self._fetch_otp(from_filter)
                if otp:
                    logger.info(f"Found OTP: {otp}")
                    return otp
            except Exception as e:
                logger.debug(f"Email check error: {e}")
            
            await asyncio.sleep(5)
        
        return None
    
    async def _fetch_otp(self, from_filter: str = None) -> Optional[str]:
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.email, self.password)
        mail.select('INBOX')
        
        since = (datetime.utcnow() - timedelta(minutes=5)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE {since} UNSEEN)')
        
        if status != 'OK':
            mail.close()
            mail.logout()
            return None
        
        for eid in reversed(messages[0].split()):
            status, data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue
            
            msg = email.message_from_bytes(data[0][1])
            
            from_addr = msg.get('From', '')
            if from_filter and from_filter.lower() not in from_addr.lower():
                continue
            
            body = self._get_body(msg)
            
            for pattern in self.otp_patterns:
                match = pattern.search(body)
                if match:
                    otp = match.group(1)
                    if 4 <= len(otp) <= 8:
                        mail.store(eid, '+FLAGS', '\\Seen')
                        mail.close()
                        mail.logout()
                        return otp
        
        mail.close()
        mail.logout()
        return None
    
    def _get_body(self, msg) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        continue
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            return ""
    
    async def get_latest_emails(self, count: int = 10) -> List[Dict]:
        if not self.password:
            return []
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select('INBOX')
            
            status, messages = mail.search(None, 'ALL')
            ids = messages[0].split()[-count:]
            
            emails = []
            for eid in reversed(ids):
                status, data = mail.fetch(eid, '(RFC822)')
                if status != 'OK':
                    continue
                
                msg = email.message_from_bytes(data[0][1])
                emails.append({
                    "from": msg.get('From', ''),
                    "subject": msg.get('Subject', ''),
                    "date": msg.get('Date', ''),
                    "body": self._get_body(msg)[:500]
                })
            
            mail.close()
            mail.logout()
            return emails
        except:
            return []


otp_handler = EmailOTPChecker()
