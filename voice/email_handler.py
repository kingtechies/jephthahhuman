import asyncio
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from config.settings import config


class EmailClient:
    def __init__(self):
        self.email = config.identity.email
        self.password = config.identity.email_password
        self.smtp_server = "mail.jephthahameh.cfd"
        self.smtp_port = 587
        self.imap_server = "mail.jephthahameh.cfd"
        self.imap_port = 993
        
    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        if not self.password:
            logger.warning("Email password not set")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email
            msg["To"] = to
            msg["Subject"] = subject
            
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to: {to}")
            return True
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
    
    async def send_bulk(self, recipients: List[str], subject: str, body: str, delay: int = 30) -> int:
        sent = 0
        for recipient in recipients:
            if await self.send_email(recipient, subject, body):
                sent += 1
            await asyncio.sleep(delay)
        return sent
    
    async def get_inbox(self, limit: int = 20, unread_only: bool = False) -> List[Dict]:
        if not self.password:
            return []
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select("INBOX")
            
            criteria = "UNSEEN" if unread_only else "ALL"
            status, messages = mail.search(None, criteria)
            
            if status != "OK":
                mail.close()
                mail.logout()
                return []
            
            ids = messages[0].split()[-limit:]
            emails = []
            
            for eid in reversed(ids):
                status, data = mail.fetch(eid, "(RFC822)")
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(data[0][1])
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            except:
                                pass
                            break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except:
                        pass
                
                emails.append({
                    "id": eid.decode(),
                    "from": msg.get("From", ""),
                    "to": msg.get("To", ""),
                    "subject": msg.get("Subject", ""),
                    "date": msg.get("Date", ""),
                    "body": body[:2000]
                })
            
            mail.close()
            mail.logout()
            return emails
        except Exception as e:
            logger.error(f"Inbox error: {e}")
            return []
    
    async def reply(self, original_email: Dict, reply_body: str) -> bool:
        to = original_email.get("from", "")
        subject = "Re: " + original_email.get("subject", "")
        
        body = f"{reply_body}\n\n---\nOn {original_email.get('date')}, {to} wrote:\n{original_email.get('body', '')[:500]}"
        
        return await self.send_email(to, subject, body)
    
    async def forward(self, original_email: Dict, to: str, note: str = "") -> bool:
        subject = "Fwd: " + original_email.get("subject", "")
        body = f"{note}\n\n--- Forwarded message ---\nFrom: {original_email.get('from')}\nDate: {original_email.get('date')}\nSubject: {original_email.get('subject')}\n\n{original_email.get('body', '')}"
        
        return await self.send_email(to, subject, body)
    
    async def delete(self, email_id: str) -> bool:
        if not self.password:
            return False
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select("INBOX")
            mail.store(email_id.encode(), "+FLAGS", "\\Deleted")
            mail.expunge()
            mail.close()
            mail.logout()
            return True
        except:
            return False
    
    async def mark_read(self, email_id: str) -> bool:
        if not self.password:
            return False
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select("INBOX")
            mail.store(email_id.encode(), "+FLAGS", "\\Seen")
            mail.close()
            mail.logout()
            return True
        except:
            return False
    
    async def auto_respond(self, keywords: Dict[str, str]) -> int:
        emails = await self.get_inbox(unread_only=True)
        responded = 0
        
        for em in emails:
            subject = em.get("subject", "").lower()
            body = em.get("body", "").lower()
            
            for keyword, response in keywords.items():
                if keyword in subject or keyword in body:
                    if await self.reply(em, response):
                        await self.mark_read(em["id"])
                        responded += 1
                    break
        
        return responded


email_client = EmailClient()
