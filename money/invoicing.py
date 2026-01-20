"""
Jephthah Invoice & Payment System
Professional invoice generation with multiple payment methods
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from config.settings import DATA_DIR


class PaymentDetails:
    """All payment method details"""
    
    # Nigerian Naira Account
    NAIRA = {
        "currency": "NGN",
        "bank_name": "Moniepoint",
        "account_name": "Jephthah Ameh",
        "account_number": "9017599903",
    }
    
    # US Dollar Account
    USD = {
        "currency": "USD",
        "bank_name": "Lead Bank",
        "account_holder": "Jephthah Gift Ameh",
        "account_number": "21832066130",
        "routing_number": "101019644",
        "account_type": "Checking",
        "bank_address": "1801 Main St, Kansas City, MO 64108",
    }
    
    # Crypto Wallets
    CRYPTO = {
        "btc_address": "bc1qpuucy0rz2qxqwc2quhva2gznmdkn9hfur75re9",
        "eth_address": "0xE7648CAd951e53FbCB6D29adCaf27eA946cC9B24",
        "sol_address": "CLJmYam1vqnUXVYpQfadkhkMS3bamGYVGWNrwdY2UsJC",
    }


class InvoiceGenerator:
    """Generate professional invoices"""
    
    def __init__(self):
        self.invoices_dir = DATA_DIR / "invoices"
        self.invoices_dir.mkdir(parents=True, exist_ok=True)
        self.invoices_db = DATA_DIR / "invoices.json"
        self.invoices = self._load_invoices()
    
    def _load_invoices(self) -> Dict:
        try:
            if self.invoices_db.exists():
                with open(self.invoices_db, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_invoices(self):
        with open(self.invoices_db, 'w') as f:
            json.dump(self.invoices, f, indent=2)
    
    async def create_invoice(
        self,
        client_name: str,
        client_email: str,
        description: str,
        amount: float,
        currency: str = "USD",
        due_days: int = 7
    ) -> Dict:
        """Create a professional invoice and email to client"""
        
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        created_at = datetime.utcnow()
        due_date = created_at + timedelta(days=due_days)
        
        invoice = {
            "id": invoice_id,
            "client_name": client_name,
            "client_email": client_email,
            "description": description,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "created_at": created_at.isoformat(),
            "due_date": due_date.isoformat(),
            "payment_received": False,
            "payment_method": None,
            "payment_date": None,
        }
        
        # Generate HTML invoice
        html_path = self._generate_html(invoice)
        invoice["html_path"] = str(html_path)
        
        # Generate PDF from HTML
        pdf_path = self._generate_pdf(html_path, invoice["id"])
        invoice["pdf_path"] = str(pdf_path) if pdf_path else None
        
        # Store invoice
        self.invoices[invoice_id] = invoice
        self._save_invoices()
        
        # Auto-email invoice to client
        await self._send_invoice_email(invoice, pdf_path or html_path)
        
        logger.info(f"📄 Invoice created and emailed: {invoice_id} for {client_name} - {currency} {amount}")
        return invoice
    
    def _generate_html(self, invoice: Dict) -> Path:
        """Generate professional HTML invoice"""
        
        # Get payment details based on currency
        if invoice["currency"] == "NGN":
            bank_info = f"""
            <h3>Nigerian Naira (NGN) Payment</h3>
            <p><strong>Bank:</strong> {PaymentDetails.NAIRA['bank_name']}</p>
            <p><strong>Account Name:</strong> {PaymentDetails.NAIRA['account_name']}</p>
            <p><strong>Account Number:</strong> {PaymentDetails.NAIRA['account_number']}</p>
            """
        else:
            bank_info = f"""
            <h3>US Dollar (USD) Payment</h3>
            <p><strong>Bank:</strong> {PaymentDetails.USD['bank_name']}</p>
            <p><strong>Account Holder:</strong> {PaymentDetails.USD['account_holder']}</p>
            <p><strong>Account Number:</strong> {PaymentDetails.USD['account_number']}</p>
            <p><strong>ACH Routing:</strong> {PaymentDetails.USD['routing_number']}</p>
            <p><strong>Account Type:</strong> {PaymentDetails.USD['account_type']}</p>
            <p><strong>Bank Address:</strong> {PaymentDetails.USD['bank_address']}</p>
            """
        
        # Crypto payment info
        crypto_info = ""
        if PaymentDetails.CRYPTO["btc_address"]:
            crypto_info = f"""
            <h3>Cryptocurrency Payment</h3>
            <p><strong>Bitcoin (BTC):</strong> <code>{PaymentDetails.CRYPTO['btc_address']}</code></p>
            <p><strong>Ethereum (ETH):</strong> <code>{PaymentDetails.CRYPTO['eth_address']}</code></p>
            <p><strong>Solana (SOL):</strong> <code>{PaymentDetails.CRYPTO['sol_address']}</code></p>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice {invoice['id']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 40px; }}
        .invoice {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
        .logo {{ font-size: 28px; font-weight: bold; color: #2563eb; }}
        .invoice-title {{ text-align: right; }}
        .invoice-title h1 {{ color: #1e3a5f; font-size: 32px; }}
        .invoice-title p {{ color: #666; }}
        .details {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
        .details-section {{ flex: 1; }}
        .details-section h3 {{ color: #2563eb; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; }}
        .details-section p {{ color: #333; margin: 5px 0; }}
        .items {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        .items th {{ background: #2563eb; color: white; padding: 15px; text-align: left; }}
        .items td {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .items .total {{ font-weight: bold; font-size: 18px; background: #f8f9fa; }}
        .payment-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .payment-section h3 {{ color: #2563eb; margin-bottom: 15px; }}
        .payment-section p {{ margin: 8px 0; color: #333; }}
        code {{ background: #e2e8f0; padding: 3px 8px; border-radius: 4px; font-family: monospace; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
        .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; text-transform: uppercase; font-size: 12px; }}
        .status.pending {{ background: #fef3c7; color: #92400e; }}
        .status.paid {{ background: #d1fae5; color: #065f46; }}
    </style>
</head>
<body>
    <div class="invoice">
        <div class="header">
            <div class="logo">JEPHTHAH TECH</div>
            <div class="invoice-title">
                <h1>INVOICE</h1>
                <p>{invoice['id']}</p>
                <span class="status pending">PENDING</span>
            </div>
        </div>
        
        <div class="details">
            <div class="details-section">
                <h3>From</h3>
                <p><strong>Jephthah Ameh</strong></p>
                <p>Full-Stack Developer</p>
                <p>hireme@jephthahameh.cfd</p>
                <p>jephthahameh.cfd</p>
            </div>
            <div class="details-section">
                <h3>Bill To</h3>
                <p><strong>{invoice['client_name']}</strong></p>
                <p>{invoice['client_email']}</p>
            </div>
            <div class="details-section">
                <h3>Invoice Details</h3>
                <p><strong>Date:</strong> {invoice['created_at'][:10]}</p>
                <p><strong>Due:</strong> {invoice['due_date'][:10]}</p>
                <p><strong>Currency:</strong> {invoice['currency']}</p>
            </div>
        </div>
        
        <table class="items">
            <tr>
                <th>Description</th>
                <th style="text-align: right;">Amount</th>
            </tr>
            <tr>
                <td>{invoice['description']}</td>
                <td style="text-align: right;">{invoice['currency']} {invoice['amount']:,.2f}</td>
            </tr>
            <tr class="total">
                <td>Total Due</td>
                <td style="text-align: right;">{invoice['currency']} {invoice['amount']:,.2f}</td>
            </tr>
        </table>
        
        <div class="payment-section">
            <h2 style="color: #1e3a5f; margin-bottom: 20px;">Payment Methods</h2>
            {bank_info}
            {crypto_info}
        </div>
        
        <div class="footer">
            <p>Thank you for your business!</p>
            <p>Questions? Contact hireme@jephthahameh.cfd</p>
        </div>
    </div>
</body>
</html>"""
        
        filepath = self.invoices_dir / f"{invoice['id']}.html"
        filepath.write_text(html)
        return filepath
    
    def _generate_pdf(self, html_path: Path, invoice_id: str) -> Optional[Path]:
        """Convert HTML invoice to PDF"""
        try:
            from weasyprint import HTML
            pdf_path = self.invoices_dir / f"{invoice_id}.pdf"
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            logger.info(f"📄 PDF generated: {pdf_path}")
            return pdf_path
        except ImportError:
            logger.warning("weasyprint not installed, falling back to HTML only")
            return None
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            return None
    
    async def _send_invoice_email(self, invoice: Dict, attachment_path: Path):
        """Send invoice to client via email"""
        try:
            from voice.email_handler import email_client
            from voice.bestie import bestie
            
            client_email = invoice["client_email"]
            client_name = invoice["client_name"]
            invoice_id = invoice["id"]
            amount = invoice["amount"]
            currency = invoice["currency"]
            description = invoice["description"]
            due_date = invoice["due_date"][:10]
            
            # Professional email body
            subject = f"Invoice {invoice_id} - {description}"
            
            body = f"""Dear {client_name},

Please find attached your invoice for the following service:

📄 Invoice: {invoice_id}
📝 Description: {description}
💰 Amount Due: {currency} {amount:,.2f}
📅 Due Date: {due_date}

Payment Methods:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏦 USD Bank Transfer:
   Bank: Lead Bank
   Account Holder: Jephthah Gift Ameh
   Account Number: 21832066130
   ACH Routing: 101019644

🇳🇬 Nigerian Naira (NGN):
   Bank: Moniepoint
   Account Name: Jephthah Ameh
   Account Number: 9017599903

₿ Cryptocurrency:
   BTC: bc1qpuucy0rz2qxqwc2quhva2gznmdkn9hfur75re9
   ETH: 0xE7648CAd951e53FbCB6D29adCaf27eA946cC9B24
   SOL: CLJmYam1vqnUXVYpQfadkhkMS3bamGYVGWNrwdY2UsJC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Once payment is made, please reply to this email with proof of payment.

Thank you for your business!

Best regards,
Jephthah Ameh
Full-Stack Developer
jephthahameh.cfd
hireme@jephthahameh.cfd"""
            
            # Send email with attachment
            success = await email_client.send_email_with_attachment(
                to_email=client_email,
                subject=subject,
                body=body,
                attachment_path=str(attachment_path)
            )
            
            if success:
                logger.info(f"✉️ Invoice emailed to {client_email}")
                # Notify owner on Telegram
                await bestie.send(
                    f"📄 **Invoice Sent**\n\n"
                    f"To: {client_name} ({client_email})\n"
                    f"Amount: {currency} {amount:,.2f}\n"
                    f"ID: {invoice_id}"
                )
            else:
                logger.error(f"Failed to email invoice to {client_email}")
                
        except Exception as e:
            logger.error(f"Invoice email error: {e}")
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict]:
        return self.invoices.get(invoice_id)
    
    def mark_paid(self, invoice_id: str, payment_method: str) -> bool:
        """Mark invoice as paid"""
        if invoice_id in self.invoices:
            self.invoices[invoice_id]["status"] = "paid"
            self.invoices[invoice_id]["payment_received"] = True
            self.invoices[invoice_id]["payment_method"] = payment_method
            self.invoices[invoice_id]["payment_date"] = datetime.utcnow().isoformat()
            self._save_invoices()
            logger.info(f"✅ Invoice {invoice_id} marked as PAID via {payment_method}")
            return True
        return False
    
    def get_pending_invoices(self) -> list:
        """Get all pending invoices"""
        return [inv for inv in self.invoices.values() if inv["status"] == "pending"]
    
    def get_invoice_summary(self, invoice_id: str) -> str:
        """Get a text summary for Telegram"""
        inv = self.invoices.get(invoice_id)
        if not inv:
            return "Invoice not found"
        
        return f"""📄 **Invoice {inv['id']}**

👤 Client: {inv['client_name']}
📧 Email: {inv['client_email']}
💰 Amount: {inv['currency']} {inv['amount']:,.2f}
📝 Description: {inv['description']}
📅 Due: {inv['due_date'][:10]}
📊 Status: {'✅ PAID' if inv['payment_received'] else '⏳ PENDING'}
"""


class PaymentVerifier:
    """Handle payment verification via Telegram"""
    
    def __init__(self, invoice_generator: InvoiceGenerator):
        self.invoices = invoice_generator
        self.pending_verifications = {}  # invoice_id -> verification request
    
    async def request_verification(self, invoice_id: str, claimed_amount: float, 
                                   payment_method: str) -> Dict:
        """Create a verification request for the owner"""
        
        inv = self.invoices.get_invoice(invoice_id)
        if not inv:
            return {"error": "Invoice not found"}
        
        verification = {
            "invoice_id": invoice_id,
            "claimed_amount": claimed_amount,
            "payment_method": payment_method,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        
        self.pending_verifications[invoice_id] = verification
        return verification
    
    def get_telegram_message(self, invoice_id: str, claimed_amount: float, 
                            payment_method: str) -> str:
        """Generate Telegram message for payment verification"""
        
        inv = self.invoices.get_invoice(invoice_id)
        if not inv:
            return "Invoice not found"
        
        return f"""💰 **PAYMENT VERIFICATION REQUEST**

📄 Invoice: {invoice_id}
👤 Client: {inv['client_name']}
💵 Invoice Amount: {inv['currency']} {inv['amount']:,.2f}
💳 Claimed Payment: {inv['currency']} {claimed_amount:,.2f}
🏦 Method: {payment_method}
⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

**Have you received this payment?**"""
    
    async def confirm_payment(self, invoice_id: str, payment_method: str) -> bool:
        """Confirm payment was received"""
        success = self.invoices.mark_paid(invoice_id, payment_method)
        if invoice_id in self.pending_verifications:
            self.pending_verifications[invoice_id]["status"] = "confirmed"
        return success
    
    async def reject_payment(self, invoice_id: str) -> bool:
        """Reject payment claim"""
        if invoice_id in self.pending_verifications:
            self.pending_verifications[invoice_id]["status"] = "rejected"
            return True
        return False


# Global instances
invoice_generator = InvoiceGenerator()
payment_verifier = PaymentVerifier(invoice_generator)
