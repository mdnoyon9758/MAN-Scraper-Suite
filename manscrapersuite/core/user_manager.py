#!/usr/bin/env python3
"""
User Management System for OmniScraper
Handles user authentication, activity tracking, and security monitoring
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests

try:
    import gspread
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

@dataclass
class UserTier:
    """User tier configuration"""
    name: str
    daily_requests: int
    concurrent_sessions: int
    features: List[str]

class UserManager:
    """Complete user management system using Google Sheets"""
    
    # User tier definitions
    TIERS = {
        'free': UserTier(
            name='Free',
            daily_requests=50,
            concurrent_sessions=1,
            features=['basic_scraping', 'csv_export']
        ),
        'pro': UserTier(
            name='Pro',
            daily_requests=500,
            concurrent_sessions=2,
            features=['basic_scraping', 'csv_export', 'json_export', 'excel_export', 'google_sheets']
        ),
        'advanced': UserTier(
            name='Advanced',
            daily_requests=-1,  # Unlimited
            concurrent_sessions=5,
            features=['all']
        )
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.spreadsheet = None
        self.user_sessions = {}  # Track active sessions
        
        if GSPREAD_AVAILABLE and config.get('google_sheets', {}).get('enabled', False):
            self._initialize_client()
            if self.client:
                self._setup_spreadsheets()
        else:
            print("⚠️ Google Sheets integration not available or not enabled")
    
    def _initialize_client(self):
        """Initialize Google Sheets client"""
        try:
            # Try service account first
            service_account_file = self.config.get("google_sheets", {}).get("service_account_file")
            if service_account_file and Path(service_account_file).exists():
                from google.oauth2.service_account import Credentials as ServiceAccountCredentials
                credentials = ServiceAccountCredentials.from_service_account_file(
                    service_account_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                )
                self.client = gspread.authorize(credentials)
            else:
                # Use OAuth 2.0
                credentials_file = self.config.get("google_sheets", {}).get("credentials_file")
                if credentials_file and Path(credentials_file).exists():
                    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                    
                    creds = None
                    token_file = Path(credentials_file).parent / "token.json"
                    
                    if token_file.exists():
                        creds = Credentials.from_authorized_user_file(str(token_file), scopes)
                    
                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                            creds = flow.run_local_server(port=0)
                        
                        with open(token_file, 'w') as token:
                            token.write(creds.to_json())
                    
                    self.client = gspread.authorize(creds)
            
            print("✅ User Management system initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize User Management: {e}")
    
    def _setup_spreadsheets(self):
        """Setup or open the user management spreadsheet"""
        if not self.client:
            return
        
        try:
            # Try to open existing spreadsheet
            try:
                self.spreadsheet = self.client.open("Man scraper suite - Management")
                print("✅ Opened existing user management spreadsheet")
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                self.spreadsheet = self.client.create("man scraper suite - management")
                print("✅ Created new user management spreadsheet")
            
            # Setup worksheets
            self._setup_users_sheet()
            self._setup_activity_sheet()
            self._setup_banned_users_sheet()
            self._setup_sessions_sheet()
            self._setup_contact_sheet()
            
        except Exception as e:
            print(f"❌ Failed to setup spreadsheets: {e}")
    
    def _setup_users_sheet(self):
        """Setup users worksheet with proper headers"""
        try:
            try:
                worksheet = self.spreadsheet.worksheet("Users")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet("Users", rows=1000, cols=10)
            
            # Check if headers exist
            if not worksheet.row_values(1):
                headers = [
                    "Email", "Registration_Date", "User_Type", "IP_Addresses", 
                    "Last_Login", "Requests_Today", "Total_Requests", 
                    "Device_Count", "Status", "Notes"
                ]
                worksheet.append_row(headers)
                print("✅ Users sheet headers created")
                
        except Exception as e:
            print(f"❌ Failed to setup users sheet: {e}")
    
    def _setup_activity_sheet(self):
        """Setup activity logging worksheet"""
        try:
            try:
                worksheet = self.spreadsheet.worksheet("Activity")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet("Activity", rows=5000, cols=8)
            
            if not worksheet.row_values(1):
                headers = [
                    "Timestamp", "User_Email", "IP_Address", "Search_Platform", 
                    "Search_Topic", "Result", "Reason", "Device_ID"
                ]
                worksheet.append_row(headers)
                print("✅ Activity sheet headers created")
                
        except Exception as e:
            print(f"❌ Failed to setup activity sheet: {e}")
    
    def _setup_banned_users_sheet(self):
        """Setup banned users worksheet"""
        try:
            try:
                worksheet = self.spreadsheet.worksheet("Banned_Users")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet("Banned_Users", rows=1000, cols=7)
            
            if not worksheet.row_values(1):
                headers = [
                    "Email", "Original_Registration", "Ban_Date", "Reason", 
                    "IP_Addresses", "Total_Requests", "Admin_Notes"
                ]
                worksheet.append_row(headers)
                print("✅ Banned users sheet headers created")
                
        except Exception as e:
            print(f"❌ Failed to setup banned users sheet: {e}")
    
    def _setup_sessions_sheet(self):
        """Setup active sessions tracking"""
        try:
            try:
                worksheet = self.spreadsheet.worksheet("Active_Sessions")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet("Active_Sessions", rows=1000, cols=6)
            
            if not worksheet.row_values(1):
                headers = [
                    "Email", "Session_ID", "Device_ID", "IP_Address", "Login_Time", "Last_Activity"
                ]
                worksheet.append_row(headers)
                print("✅ Sessions sheet headers created")
                
        except Exception as e:
            print(f"❌ Failed to setup sessions sheet: {e}")
    
    def _setup_contact_sheet(self):
        """Setup contact messages worksheet"""
        try:
            try:
                worksheet = self.spreadsheet.worksheet("Contact")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet("Contact", rows=2000, cols=6)
            
            if not worksheet.row_values(1):
                headers = [
                    "Name", "Email", "Phone", "Message", "Timestamp", "IP_Address"
                ]
                worksheet.append_row(headers)
                print("✅ Contact sheet headers created")
                
        except Exception as e:
            print(f"❌ Failed to setup contact sheet: {e}")
    
    def submit_contact_message(self, name: str, email: str, phone: str, message: str, ip_address: str) -> bool:
        """Submit a contact message to Google Sheets"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            contact_sheet = self.spreadsheet.worksheet("Contact")
            
            contact_data = [
                name,
                email,
                phone,
                message,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ip_address
            ]
            
            contact_sheet.append_row(contact_data)
            print(f"✅ Contact message from {name} ({email}) submitted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to submit contact message: {e}")
            return False
    
    def get_contact_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent contact messages"""
        if not self.client or not self.spreadsheet:
            return []
        
        try:
            contact_sheet = self.spreadsheet.worksheet("Contact")
            messages = contact_sheet.get_all_records()
            
            # Sort by timestamp (most recent first) and limit
            sorted_messages = sorted(
                messages, 
                key=lambda x: x.get('Timestamp', '1970-01-01 00:00:00'), 
                reverse=True
            )
            
            return sorted_messages[:limit]
            
        except Exception as e:
            print(f"❌ Failed to get contact messages: {e}")
            return []
    
    def register_user(self, email: str, ip_address: str, device_id: str, user_type: str = 'free') -> bool:
        """Register a new user"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            # Check if user already exists
            if self.get_user(email):
                print(f"⚠️  User {email} already exists")
                return False
            
            # Check if email is banned
            if self.is_user_banned(email):
                print(f"❌ Email {email} is banned")
                return False
            
            users_sheet = self.spreadsheet.worksheet("Users")
            
            # Add new user
            user_data = [
                email,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_type,
                ip_address,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                0,  # Requests today
                0,  # Total requests
                1,  # Device count
                "active",
                "New user registration"
            ]
            
            users_sheet.append_row(user_data)
            print(f"✅ User {email} registered successfully as {user_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register user {email}: {e}")
            return False
    
    def authenticate_user(self, email: str, ip_address: str, device_id: str) -> Tuple[bool, str, Dict]:
        """Authenticate user and create session"""
        if not self.client or not self.spreadsheet:
            return False, "System unavailable", {}
        
        try:
            # Check if user is banned
            if self.is_user_banned(email):
                return False, "User is banned", {}
            
            # Get user data
            user = self.get_user(email)
            if not user:
                return False, "User not found", {}
            
            # Check device limit
            if not self._check_device_limit(email, device_id):
                return False, "Too many active devices", {}
            
            # Update user login info
            self._update_user_login(email, ip_address)
            
            # Create session
            session_id = self._create_session(email, ip_address, device_id)
            
            user_info = {
                'email': email,
                'user_type': user.get('User_Type', 'free'),
                'session_id': session_id,
                'tier': self.TIERS.get(user.get('User_Type', 'free'))
            }
            
            return True, "Authentication successful", user_info
            
        except Exception as e:
            print(f"❌ Authentication failed for {email}: {e}")
            return False, "Authentication error", {}
    
    def log_activity(self, email: str, ip_address: str, platform: str, topic: str, 
                    result: str, reason: str = "", device_id: str = "") -> bool:
        """Log user activity"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            activity_sheet = self.spreadsheet.worksheet("Activity")
            
            activity_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                ip_address,
                platform,
                topic,
                result,
                reason,
                device_id
            ]
            
            activity_sheet.append_row(activity_data)
            
            # Update user request count
            self._increment_user_requests(email)
            
            # Check for suspicious activity
            self._check_suspicious_activity(email, ip_address)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to log activity for {email}: {e}")
            return False
    
    def check_user_limits(self, email: str) -> Dict[str, Any]:
        """Check if user has exceeded their limits"""
        user = self.get_user(email)
        if not user:
            return {'allowed': False, 'reason': 'User not found'}
        
        user_type = user.get('User_Type', 'free')
        tier = self.TIERS.get(user_type, self.TIERS['free'])
        
        # Check daily requests
        requests_today = int(user.get('Requests_Today', 0))
        
        if tier.daily_requests > 0 and requests_today >= tier.daily_requests:
            return {
                'allowed': False, 
                'reason': f'Daily limit exceeded ({requests_today}/{tier.daily_requests})',
                'requests_today': requests_today,
                'daily_limit': tier.daily_requests
            }
        
        return {
            'allowed': True,
            'requests_today': requests_today,
            'daily_limit': tier.daily_requests,
            'tier': tier.name
        }
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user information"""
        if not self.client or not self.spreadsheet:
            return None
        
        try:
            users_sheet = self.spreadsheet.worksheet("Users")
            users = users_sheet.get_all_records()
            
            for user in users:
                if user.get('Email') == email:
                    return user
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get user {email}: {e}")
            return None
    
    def is_user_banned(self, email: str) -> bool:
        """Check if user is banned by searching only email column"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            banned_sheet = self.spreadsheet.worksheet("Banned_Users")
            # Get only the email column (column A) to reduce API calls
            email_values = banned_sheet.col_values(1)[1:]  # Skip header
            
            return email in email_values
            
        except Exception as e:
            print(f"❌ Failed to check ban status for {email}: {e}")
            return False
    
    def ban_user(self, email: str, reason: str, admin_notes: str = "") -> bool:
        """Ban a user and move to banned users sheet"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            user = self.get_user(email)
            if not user:
                return False
            
            # Add to banned users
            banned_sheet = self.spreadsheet.worksheet("Banned_Users")
            banned_data = [
                email,
                user.get('Registration_Date', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                reason,
                user.get('IP_Addresses', ''),
                user.get('Total_Requests', 0),
                admin_notes
            ]
            banned_sheet.append_row(banned_data)
            
            # Remove from active users
            users_sheet = self.spreadsheet.worksheet("Users")
            users = users_sheet.get_all_records()
            
            for i, user_record in enumerate(users):
                if user_record.get('Email') == email:
                    users_sheet.delete_rows(i + 2)  # +2 because of 1-indexing and header
                    break
            
            # Remove active sessions
            self._remove_user_sessions(email)
            
            print(f"✅ User {email} banned successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to ban user {email}: {e}")
            return False
    
    def weekly_backup_and_cleanup(self) -> bool:
        """Weekly backup of activity data and cleanup"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            activity_sheet = self.spreadsheet.worksheet("Activity")
            
            # Export current data
            all_data = activity_sheet.get_all_values()
            
            if len(all_data) > 1:  # More than just headers
                # Create backup file name with timestamp
                backup_filename = f"Activity_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                # Convert to CSV format
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerows(all_data)
                csv_content = output.getvalue()
                
                # Save to Google Drive (using cloud uploader)
                from ..exporters.cloud_uploader import CloudUploader
                uploader = CloudUploader(self.config)
                
                # Create temporary file
                backup_file = Path(f"temp_{backup_filename}")
                backup_file.write_text(csv_content, encoding='utf-8')
                
                # Upload to Drive
                result = uploader.upload_to_google_drive(backup_file)
                backup_file.unlink()  # Delete temp file
                
                if result:
                    # Clear activity sheet but keep headers
                    headers = all_data[0] if all_data else []
                    activity_sheet.clear()
                    if headers:
                        activity_sheet.append_row(headers)
                    
                    print(f"✅ Activity backup completed: {backup_filename}")
                    return True
            
            print("⚠️  No activity data to backup")
            return True
            
        except Exception as e:
            print(f"❌ Failed to backup activities: {e}")
            return False
    
    def _check_device_limit(self, email: str, device_id: str) -> bool:
        """Check if user has exceeded device limit"""
        try:
            user = self.get_user(email)
            if not user:
                return False
            
            user_type = user.get('User_Type', 'free')
            tier = self.TIERS.get(user_type, self.TIERS['free'])
            
            # Get active sessions
            sessions_sheet = self.spreadsheet.worksheet("Active_Sessions")
            sessions = sessions_sheet.get_all_records()
            
            active_devices = set()
            current_time = datetime.now()
            
            for session in sessions:
                if session.get('Email') == email:
                    # Check if session is still active (within last hour)
                    last_activity = datetime.strptime(
                        session.get('Last_Activity', '1970-01-01 00:00:00'), 
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if current_time - last_activity < timedelta(hours=1):
                        active_devices.add(session.get('Device_ID'))
            
            # Allow if under limit or if it's the same device
            return len(active_devices) < tier.concurrent_sessions or device_id in active_devices
            
        except Exception as e:
            print(f"❌ Failed to check device limit: {e}")
            return True  # Allow on error
    
    def _create_session(self, email: str, ip_address: str, device_id: str) -> str:
        """Create a new user session"""
        try:
            session_id = hashlib.md5(f"{email}_{device_id}_{datetime.now()}".encode()).hexdigest()
            
            sessions_sheet = self.spreadsheet.worksheet("Active_Sessions")
            
            session_data = [
                email,
                session_id,
                device_id,
                ip_address,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            sessions_sheet.append_row(session_data)
            return session_id
            
        except Exception as e:
            print(f"❌ Failed to create session: {e}")
            return ""
    
    def _update_user_login(self, email: str, ip_address: str):
        """Update user login information"""
        try:
            users_sheet = self.spreadsheet.worksheet("Users")
            users = users_sheet.get_all_records()
            
            for i, user in enumerate(users):
                if user.get('Email') == email:
                    row_num = i + 2  # +2 for 1-indexing and header
                    
                    # Update last login
                    users_sheet.update_cell(row_num, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # Update IP addresses if new
                    current_ips = user.get('IP_Addresses', '')
                    if ip_address not in current_ips:
                        new_ips = f"{current_ips},{ip_address}" if current_ips else ip_address
                        users_sheet.update_cell(row_num, 4, new_ips)
                    
                    break
                    
        except Exception as e:
            print(f"❌ Failed to update user login: {e}")
    
    def _increment_user_requests(self, email: str):
        """Increment user request counters"""
        try:
            users_sheet = self.spreadsheet.worksheet("Users")
            users = users_sheet.get_all_records()
            
            for i, user in enumerate(users):
                if user.get('Email') == email:
                    row_num = i + 2
                    
                    # Reset daily counter if it's a new day
                    today = datetime.now().strftime("%Y-%m-%d")
                    last_login = user.get('Last_Login', '')
                    
                    if not last_login.startswith(today):
                        users_sheet.update_cell(row_num, 6, 1)  # Reset daily requests
                    else:
                        current_daily = int(user.get('Requests_Today', 0))
                        users_sheet.update_cell(row_num, 6, current_daily + 1)
                    
                    # Increment total requests
                    current_total = int(user.get('Total_Requests', 0))
                    users_sheet.update_cell(row_num, 7, current_total + 1)
                    
                    break
                    
        except Exception as e:
            print(f"❌ Failed to increment user requests: {e}")
    
    def _check_suspicious_activity(self, email: str, ip_address: str):
        """Check for suspicious activity patterns"""
        try:
            # Get recent activity for this user
            activity_sheet = self.spreadsheet.worksheet("Activity")
            activities = activity_sheet.get_all_records()
            
            recent_activities = []
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            for activity in activities:
                if activity.get('User_Email') == email:
                    activity_time = datetime.strptime(
                        activity.get('Timestamp', '1970-01-01 00:00:00'),
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if activity_time > cutoff_time:
                        recent_activities.append(activity)
            
            # Check for rapid IP switching (more than 3 IPs in 1 hour)
            recent_ips = set(activity.get('IP_Address') for activity in recent_activities)
            if len(recent_ips) > 3:
                self.ban_user(email, "Suspicious IP switching", f"Used {len(recent_ips)} IPs in 1 hour")
                return
            
            # Check for excessive requests (more than 100 in 1 hour for free users)
            user = self.get_user(email)
            if user and user.get('User_Type') == 'free' and len(recent_activities) > 100:
                self.ban_user(email, "Excessive requests", f"{len(recent_activities)} requests in 1 hour")
                return
                
        except Exception as e:
            print(f"❌ Failed to check suspicious activity: {e}")
    
    def _remove_user_sessions(self, email: str):
        """Remove all sessions for a user"""
        try:
            sessions_sheet = self.spreadsheet.worksheet("Active_Sessions")
            sessions = sessions_sheet.get_all_records()
            
            # Remove sessions in reverse order to maintain row indices
            for i in reversed(range(len(sessions))):
                if sessions[i].get('Email') == email:
                    sessions_sheet.delete_rows(i + 2)  # +2 for 1-indexing and header
                    
        except Exception as e:
            print(f"❌ Failed to remove user sessions: {e}")
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get overall user statistics"""
        if not self.client or not self.spreadsheet:
            return {}
        
        try:
            users_sheet = self.spreadsheet.worksheet("Users")
            banned_sheet = self.spreadsheet.worksheet("Banned_Users")
            activity_sheet = self.spreadsheet.worksheet("Activity")
            
            users = users_sheet.get_all_records()
            banned_users = banned_sheet.get_all_records()
            activities = activity_sheet.get_all_records()
            
            # Count by user type
            user_types = {}
            for user in users:
                user_type = user.get('User_Type', 'free')
                user_types[user_type] = user_types.get(user_type, 0) + 1
            
            # Recent activity (last 24 hours)
            recent_activity_count = 0
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for activity in activities:
                try:
                    activity_time = datetime.strptime(
                        activity.get('Timestamp', '1970-01-01 00:00:00'),
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if activity_time > cutoff_time:
                        recent_activity_count += 1
                except:
                    continue
            
            return {
                'total_users': len(users),
                'banned_users': len(banned_users),
                'user_types': user_types,
                'total_activities': len(activities),
                'recent_activities_24h': recent_activity_count
            }
            
        except Exception as e:
            print(f"❌ Failed to get user stats: {e}")
            return {}
