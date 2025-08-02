#!/usr/bin/env python3
"""
Notification Manager
Handles email and Telegram notifications for OmniScraper
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

class NotificationManager:
    """Manages email and Telegram notifications"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.email_config = config["notifications"]["email"]
        self.telegram_config = config["notifications"]["telegram"]
    
    def send_email(self, subject: str, body: str, recipients: Optional[List[str]] = None, 
                   attachments: Optional[List[Path]] = None) -> bool:
        """Send email notification"""
        if not self.email_config["enabled"]:
            print("Email notifications are disabled")
            return False
        
        if not recipients:
            recipients = self.email_config["recipients"]
        
        if not recipients:
            print("No email recipients configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.email_config["username"]
            message["To"] = ", ".join(recipients)
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if attachment_path.exists():
                        with open(attachment_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment_path.name}'
                        )
                        message.attach(part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(self.email_config["username"], self.email_config["password"])
                server.sendmail(self.email_config["username"], recipients, message.as_string())
            
            print(f"Email sent successfully to {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_telegram_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """Send Telegram notification"""
        if not self.telegram_config["enabled"]:
            print("Telegram notifications are disabled")
            return False
        
        bot_token = self.telegram_config["bot_token"]
        if not bot_token:
            print("Telegram bot token not configured")
            return False
        
        if not chat_id:
            chat_id = self.telegram_config["chat_id"]
        
        if not chat_id:
            print("Telegram chat ID not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            print("Telegram message sent successfully")
            return True
            
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    def send_telegram_document(self, document_path: Path, caption: str = "", 
                             chat_id: Optional[str] = None) -> bool:
        """Send document via Telegram"""
        if not self.telegram_config["enabled"]:
            print("Telegram notifications are disabled")
            return False
        
        bot_token = self.telegram_config["bot_token"]
        if not bot_token:
            print("Telegram bot token not configured")
            return False
        
        if not chat_id:
            chat_id = self.telegram_config["chat_id"]
        
        if not chat_id:
            print("Telegram chat ID not configured")
            return False
        
        if not document_path.exists():
            print(f"Document not found: {document_path}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            
            with open(document_path, 'rb') as document:
                files = {
                    'document': (document_path.name, document, 'application/octet-stream')
                }
                data = {
                    'chat_id': chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
            
            print(f"Document sent successfully: {document_path.name}")
            return True
            
        except Exception as e:
            print(f"Failed to send Telegram document: {e}")
            return False
    
    def notify_scraping_complete(self, site: str, records_count: int, 
                               output_file: Optional[Path] = None) -> bool:
        """Send notification when scraping is complete"""
        subject = f"🔥 OmniScraper: Scraping Complete - {site}"
        
        message = f"""
🔥 <b>OmniScraper Notification</b>

✅ <b>Scraping Completed Successfully</b>

📊 <b>Details:</b>
• Site: {site}
• Records scraped: {records_count:,}
• Completion time: {time.strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if output_file:
            message += f"• Output file: {output_file.name}\n"
        
        message += "\n🚀 OmniScraper - 100% Free, No Limits, All Features!"
        
        # Send via both channels if enabled
        email_sent = self.send_email(subject, message, attachments=[output_file] if output_file else None)
        telegram_sent = self.send_telegram_message(message)
        
        if output_file and telegram_sent:
            self.send_telegram_document(output_file, f"Scraped data from {site}")
        
        return email_sent or telegram_sent
    
    def notify_error(self, site: str, error_message: str) -> bool:
        """Send notification when an error occurs during scraping"""
        subject = f"❌ OmniScraper: Error - {site}"
        
        message = f"""
🔥 <b>OmniScraper Notification</b>

❌ <b>Scraping Error</b>

📊 <b>Details:</b>
• Site: {site}
• Error: {error_message}
• Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

Please check the logs for more information.

🚀 OmniScraper - 100% Free, No Limits, All Features!
"""
        
        # Send via both channels if enabled
        email_sent = self.send_email(subject, message)
        telegram_sent = self.send_telegram_message(message)
        
        return email_sent or telegram_sent
    
    def notify_scheduled_task_start(self, task_name: str) -> bool:
        """Send notification when a scheduled task starts"""
        message = f"""
🔥 <b>OmniScraper - Scheduled Task Started</b>

⏰ Task: {task_name}
🕒 Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}

🚀 OmniScraper running automatically!
"""
        
        return self.send_telegram_message(message)
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test both email and Telegram notifications"""
        results = {}
        
        test_message = f"""
🔥 <b>OmniScraper Test Notification</b>

✅ This is a test message to verify notifications are working.

📊 <b>Test Details:</b>
• Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
• Status: All systems operational

🚀 OmniScraper - 100% Free, No Limits, All Features!
"""
        
        # Test email
        if self.email_config["enabled"]:
            results["email"] = self.send_email("🔥 OmniScraper Test Email", test_message)
        else:
            results["email"] = False
            print("Email notifications disabled - skipping test")
        
        # Test Telegram
        if self.telegram_config["enabled"]:
            results["telegram"] = self.send_telegram_message(test_message)
        else:
            results["telegram"] = False
            print("Telegram notifications disabled - skipping test")
        
        return results

# Import time for timestamp functions
import time
