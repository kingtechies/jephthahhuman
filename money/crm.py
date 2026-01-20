import asyncio
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from config.settings import DATA_DIR, config

class CRMSystem:
    def __init__(self):
        self.db_path = DATA_DIR / "business.db"
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Clients table
        c.execute('''CREATE TABLE IF NOT EXISTS clients
                     (id INTEGER PRIMARY KEY, name TEXT, email TEXT, platform TEXT, 
                      notes TEXT, status TEXT, last_contact DATE, message_history TEXT)''')
                      
        # Leads table
        c.execute('''CREATE TABLE IF NOT EXISTS leads
                     (id INTEGER PRIMARY KEY, source TEXT, contact_info TEXT, 
                      potential_value REAL, status TEXT, created_at DATE)''')
                      
        # Projects table
        c.execute('''CREATE TABLE IF NOT EXISTS projects
                     (id INTEGER PRIMARY KEY, client_id INTEGER, title TEXT, 
                      deadline DATE, value REAL, status TEXT, progress INTEGER)''')
                      
        conn.commit()
        conn.close()
    
    async def add_client(self, name: str, email: str, platform: str = "direct") -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO clients (name, email, platform, status, last_contact, message_history) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, email, platform, "active", datetime.utcnow(), "[]"))
        client_id = c.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Added client: {name}")
        return client_id
    
    async def add_lead(self, source: str, contact: str, value: float) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO leads (source, contact_info, potential_value, status, created_at) VALUES (?, ?, ?, ?, ?)",
                  (source, contact, value, "new", datetime.utcnow()))
        lead_id = c.lastrowid
        conn.commit()
        conn.close()
        return lead_id
        
    async def update_status(self, table: str, id: int, status: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"UPDATE {table} SET status = ? WHERE id = ?", (status, id))
        conn.commit()
        conn.close()

    async def get_active_clients(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM clients WHERE status = 'active'")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    async def log_interaction(self, client_id: int, message: str, direction: str = "outbound"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT message_history FROM clients WHERE id = ?", (client_id,))
        row = c.fetchone()
        if row:
            history = json.loads(row[0]) if row[0] else []
            history.append({
                "date": datetime.utcnow().isoformat(),
                "direction": direction,
                "message": message
            })
            c.execute("UPDATE clients SET message_history = ?, last_contact = ? WHERE id = ?",
                      (json.dumps(history), datetime.utcnow(), client_id))
            conn.commit()
        conn.close()
    
    def get_leads(self, status: str = None, limit: int = 100) -> List[Dict]:
        """Get leads from CRM"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if status:
            c.execute("SELECT * FROM leads WHERE status = ? LIMIT ?", (status, limit))
        else:
            c.execute("SELECT * FROM leads LIMIT ?", (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            lead_dict = dict(row)
            # Parse contact_info JSON if it exists
            if lead_dict.get('contact_info'):
                try:
                    contact = json.loads(lead_dict['contact_info'])
                    if isinstance(contact, dict):
                        lead_dict['email'] = contact.get('email')
                        lead_dict['name'] = contact.get('name')
                    else:
                        lead_dict['email'] = contact
                except:
                    lead_dict['email'] = lead_dict['contact_info']
            result.append(lead_dict)
        
        return result
    
    def update_lead(self, lead_id: int, status: str):
        """Update lead status"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
        conn.commit()
        conn.close()

class FinanceManager:
    def __init__(self):
        self.db_path = DATA_DIR / "business.db"
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Invoices table
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (id INTEGER PRIMARY KEY, client_id INTEGER, amount REAL, 
                      description TEXT, due_date DATE, status TEXT, pdf_path TEXT, created_at DATE)''')
                      
        # Transactions table
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY, type TEXT, amount REAL, 
                      category TEXT, description TEXT, date DATE)''')
        
        conn.commit()
        conn.close()
    
    async def create_invoice(self, client_id: int, amount: float, description: str, due_days: int = 14) -> str:
        # Generate HTML Invoice
        invoice_html = f"""
        <html>
        <body>
            <h1>INVOICE</h1>
            <p>From: Jephthah Ameh (Jephthah Tech)</p>
            <p>To: Client #{client_id}</p>
            <hr>
            <h3>Items</h3>
            <p>{description}: ${amount:.2f}</p>
            <hr>
            <h2>Total: ${amount:.2f}</h2>
            <p>Please pay to {config.crypto.eth_wallet or "ETH Wallet"} or Bank Transfer</p>
        </body>
        </html>
        """
        
        filename = f"invoice_{client_id}_{int(datetime.now().timestamp())}.html"
        path = DATA_DIR / "invoices" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(invoice_html)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        due_date = datetime.now().timestamp() + (due_days * 86400)
        c.execute("INSERT INTO invoices (client_id, amount, description, due_date, status, pdf_path, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (client_id, amount, description, due_date, "unpaid", str(path), datetime.utcnow()))
        conn.commit()
        conn.close()
        
        logger.info(f"Invoice created: ${amount}")
        return str(path)
    
    async def record_income(self, amount: float, source: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO transactions (type, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                  ("income", amount, source, "Earnings", datetime.utcnow()))
        conn.commit()
        conn.close()
        logger.info(f"Income recorded: +${amount}")

    async def get_total_earnings(self) -> float:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
        result = c.fetchone()[0]
        conn.close()
        return result or 0.0

crm = CRMSystem()
finance = FinanceManager()
