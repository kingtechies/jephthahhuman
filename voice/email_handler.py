"""
Jephthah Email Handler
Robust email sending/receiving with retry logic and full inbox management
"""

import asyncio
import smtplib
import imaplib
import email
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import wraps
from loguru import logger

from config.settings import config


def retry_sync(max_retries: int = 3, base_delay: float = 2.0, exceptions=(Exception,)):
    """Decorator for sync retry with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay}s...")
                        import time
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
            raise last_exception
        return wrapper
    return decorator


class EmailClient:
    """Robust email client with retry logic and full inbox management"""
    
    def __init__(self):
        self.email = config.identity.email
        self.password = config.identity.email_password
        self.smtp_server = "mail.jephthahameh.cfd"
        self.smtp_port = 587
        self.imap_server = "mail.jephthahameh.cfd"
        self.imap_port = 993
        self.timeout = 30  # Increased timeout
        self._last_connection_check = None
        
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context - lenient for self-signed certs"""
        context = ssl.create_default_context()
        # Allow self-signed certificates (common for mail servers)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    @retry_sync(max_retries=3, base_delay=2.0)
    def _connect_smtp(self) -> smtplib.SMTP:
        """Connect to SMTP server with retry"""
        server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
        server.ehlo()
        server.starttls(context=self._create_ssl_context())
        server.ehlo()
        server.login(self.email, self.password)
        return server
    
    @retry_sync(max_retries=3, base_delay=2.0)
    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server with retry"""
        # Set socket timeout globally for IMAP
        import socket
        socket.setdefaulttimeout(self.timeout)
        
        mail = imaplib.IMAP4_SSL(
            self.imap_server, 
            self.imap_port, 
            ssl_context=self._create_ssl_context(),
            timeout=self.timeout
        )
        mail.login(self.email, self.password)
        return mail
    
    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Send an email with retry logic"""
        if not self.password:
            logger.warning("Email password not set in jeph.env")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Jephthah Ameh <{self.email}>"
            msg["To"] = to
            msg["Subject"] = subject
            msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            # Use sync connection with retry
            server = self._connect_smtp()
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✉️ Email sent to: {to} | Subject: {subject[:50]}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Email auth failed - check password in jeph.env: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"Could not connect to SMTP server: {e}")
            return False
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
    
    async def send_bulk(self, recipients: List[str], subject: str, body: str, delay: int = 30) -> int:
        """Send bulk emails with rate limiting"""
        sent = 0
        failed = 0
        
        for i, recipient in enumerate(recipients):
            logger.info(f"Sending email {i+1}/{len(recipients)} to {recipient}")
            if await self.send_email(recipient, subject, body):
                sent += 1
            else:
                failed += 1
            
            if i < len(recipients) - 1:
                await asyncio.sleep(delay)
        
        logger.info(f"Bulk email complete: {sent} sent, {failed} failed")
        return sent
    
    async def send_email_with_attachment(self, to_email: str, subject: str, body: str, 
                                         attachment_path: str) -> bool:
        """Send email with file attachment (PDF, HTML, etc)"""
        if not self.password:
            logger.warning("Email password not set")
            return False
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            from pathlib import Path
            
            # Create multipart message
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Attach body
            msg.attach(MIMEText(body, "plain"))
            
            # Attach file
            file_path = Path(attachment_path)
            if file_path.exists():
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={file_path.name}"
                )
                msg.attach(part)
            
            # Send
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP_SSL(self.smtp_server, 465, context=context, timeout=30) as server:
                server.login(self.email, self.password)
                server.sendmail(self.email, to_email, msg.as_string())
            
            logger.info(f"📎 Email with attachment sent to: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email with attachment error: {e}")
            return False
    
    async def get_inbox(self, limit: int = 20, unread_only: bool = False) -> List[Dict]:
        """Get inbox emails with retry logic"""
        if not self.password:
            logger.warning("Email password not set")
            return []
        
        try:
            mail = self._connect_imap()
            mail.select("INBOX")
            
            criteria = "UNSEEN" if unread_only else "ALL"
            status, messages = mail.search(None, criteria)
            
            if status != "OK":
                mail.close()
                mail.logout()
                return []
            
            ids = messages[0].split()[-limit:] if messages[0] else []
            emails = []
            
            for eid in reversed(ids):
                try:
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
                except Exception as e:
                    logger.debug(f"Error parsing email {eid}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            logger.info(f"📬 Retrieved {len(emails)} emails from inbox")
            return emails
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error - check credentials: {e}")
            return []
        except Exception as e:
            logger.error(f"Inbox error: {e}")
            return []
    
    async def read_previous_emails(self, days: int = 7, limit: int = 50) -> List[Dict]:
        """Read all emails from the past N days"""
        if not self.password:
            return []
        
        try:
            mail = self._connect_imap()
            mail.select("INBOX")
            
            # Search for emails from past N days
            since_date = (datetime.utcnow() - timedelta(days=days)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE {since_date})')
            
            if status != "OK" or not messages[0]:
                mail.close()
                mail.logout()
                return []
            
            ids = messages[0].split()[-limit:]
            emails = []
            
            for eid in reversed(ids):
                try:
                    status, data = mail.fetch(eid, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    msg = email.message_from_bytes(data[0][1])
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
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
                        "body": body,
                        "read": True  # We mark as read when fetching
                    })
                except Exception as e:
                    logger.debug(f"Error parsing email {eid}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            logger.info(f"📧 Retrieved {len(emails)} emails from past {days} days")
            return emails
            
        except Exception as e:
            logger.error(f"Read previous emails error: {e}")
            return []
    
    async def reply(self, original_email: Dict, reply_body: str) -> bool:
        """Reply to an email"""
        # Extract email address from "Name <email>" format
        from_field = original_email.get("from", "")
        if "<" in from_field and ">" in from_field:
            to = from_field[from_field.find("<")+1:from_field.find(">")]
        else:
            to = from_field
        
        subject = original_email.get("subject", "")
        if not subject.lower().startswith("re:"):
            subject = "Re: " + subject
        
        body = f"{reply_body}\n\n---\nOn {original_email.get('date')}, {from_field} wrote:\n{original_email.get('body', '')[:500]}"
        
        success = await self.send_email(to, subject, body)
        if success:
            logger.info(f"✉️ Replied to: {to}")
        return success
    
    async def forward(self, original_email: Dict, to: str, note: str = "") -> bool:
        """Forward an email"""
        subject = "Fwd: " + original_email.get("subject", "")
        body = f"{note}\n\n--- Forwarded message ---\nFrom: {original_email.get('from')}\nDate: {original_email.get('date')}\nSubject: {original_email.get('subject')}\n\n{original_email.get('body', '')}"
        
        return await self.send_email(to, subject, body)
    
    async def delete(self, email_id: str) -> bool:
        """Delete an email"""
        if not self.password:
            return False
        
        try:
            mail = self._connect_imap()
            mail.select("INBOX")
            mail.store(email_id.encode(), "+FLAGS", "\\Deleted")
            mail.expunge()
            mail.close()
            mail.logout()
            logger.info(f"🗑️ Deleted email: {email_id}")
            return True
        except Exception as e:
            logger.error(f"Delete email error: {e}")
            return False
    
    async def mark_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        if not self.password:
            return False
        
        try:
            mail = self._connect_imap()
            mail.select("INBOX")
            mail.store(email_id.encode(), "+FLAGS", "\\Seen")
            mail.close()
            mail.logout()
            return True
        except Exception as e:
            logger.error(f"Mark read error: {e}")
            return False
    
    async def auto_respond(self, keywords: Dict[str, str]) -> int:
        """Auto-respond to emails based on keywords"""
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
                        logger.info(f"Auto-replied to email about: {keyword}")
                    break
        
        return responded
    
    async def test_connection(self) -> Dict[str, bool]:
        """Test both SMTP and IMAP connections"""
        results = {"smtp": False, "imap": False, "email": self.email}
        
        try:
            self._connect_smtp().quit()
            results["smtp"] = True
            logger.info("✅ SMTP connection test passed")
        except Exception as e:
            logger.error(f"❌ SMTP test failed: {e}")
        
        try:
            mail = self._connect_imap()
            mail.logout()
            results["imap"] = True
            logger.info("✅ IMAP connection test passed")
        except Exception as e:
            logger.error(f"❌ IMAP test failed: {e}")
        
        return results


# Global email client instance
email_client = EmailClient()
