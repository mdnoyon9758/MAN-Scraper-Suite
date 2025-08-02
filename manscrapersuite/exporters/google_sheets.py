#!/usr/bin/env python3
"""
Google Sheets Integration
Complete implementation for exporting scraped data to Google Sheets
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("⚠️  Google Sheets dependencies not installed. Run: pip install gspread google-auth google-auth-oauthlib")

class GoogleSheetsExporter:
    """Export scraped data to Google Sheets"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.spreadsheet = None
        
        if GSPREAD_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client with proper authentication"""
        try:
            # Check for service account authentication first
            service_account_file = self.config.get("google_sheets", {}).get("service_account_file")
            if service_account_file and Path(service_account_file).exists():
                self._init_service_account(service_account_file)
            else:
                # Fall back to OAuth 2.0 client authentication
                credentials_file = self.config.get("google_sheets", {}).get("credentials_file")
                if credentials_file and Path(credentials_file).exists():
                    self._init_oauth_client(credentials_file)
                else:
                    print("❌ No valid Google Sheets credentials found")
                    return
            
            print("✅ Google Sheets client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets client: {e}")
    
    def _init_service_account(self, service_account_file: str):
        """Initialize with service account credentials"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_service_account_file(
            service_account_file, 
            scopes=scopes
        )
        self.client = gspread.authorize(credentials)
    
    def _init_oauth_client(self, credentials_file: str):
        """Initialize with OAuth 2.0 credentials"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = None
        token_file = Path(credentials_file).parent / "token.json"
        
        # Load existing token
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.client = gspread.authorize(creds)
    
    def create_spreadsheet(self, name: str, folder_id: Optional[str] = None) -> Optional[str]:
        """Create a new Google Spreadsheet"""
        if not self.client:
            print("❌ Google Sheets client not initialized")
            return None
        
        try:
            self.spreadsheet = self.client.create(name)
            spreadsheet_id = self.spreadsheet.id
            
            # Move to specific folder if provided
            if folder_id:
                self.client.drive.move_file(spreadsheet_id, folder_id)
            
            print(f"✅ Created spreadsheet: {name} (ID: {spreadsheet_id})")
            return spreadsheet_id
            
        except Exception as e:
            print(f"❌ Failed to create spreadsheet: {e}")
            return None
    
    def open_spreadsheet(self, spreadsheet_id: Optional[str] = None, spreadsheet_name: Optional[str] = None) -> bool:
        """Open existing spreadsheet by ID or name"""
        if not self.client:
            print("❌ Google Sheets client not initialized")
            return False
        
        try:
            if spreadsheet_id:
                self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            elif spreadsheet_name:
                self.spreadsheet = self.client.open(spreadsheet_name)
            else:
                print("❌ Must provide either spreadsheet_id or spreadsheet_name")
                return False
            
            print(f"✅ Opened spreadsheet: {self.spreadsheet.title}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to open spreadsheet: {e}")
            return False
    
    def export_data(self, data: List[Dict[str, Any]], worksheet_name: str = "Sheet1", 
                   append_mode: bool = False) -> bool:
        """Export data to Google Sheets"""
        if not self.client or not self.spreadsheet:
            print("❌ Google Sheets not properly initialized")
            return False
        
        if not data:
            print("⚠️  No data to export")
            return False
        
        try:
            # Get or create worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                if not append_mode:
                    worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            
            # Prepare data for export
            formatted_data = self._format_data_for_sheets(data)
            
            if append_mode and worksheet.row_count > 1:
                # Append to existing data
                worksheet.append_rows(formatted_data[1:])  # Skip header row
                print(f"✅ Appended {len(formatted_data)-1} rows to {worksheet_name}")
            else:
                # Replace all data
                worksheet.update('A1', formatted_data)
                print(f"✅ Exported {len(formatted_data)-1} rows to {worksheet_name}")
            
            # Auto-resize columns
            self._auto_resize_columns(worksheet)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to export data to Google Sheets: {e}")
            return False
    
    def _format_data_for_sheets(self, data: List[Dict[str, Any]]) -> List[List[str]]:
        """Format data for Google Sheets compatibility"""
        if not data:
            return []
        
        # Get all unique keys from all dictionaries
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Sort keys for consistent column order
        headers = sorted(list(all_keys))
        
        # Create rows
        formatted_data = [headers]  # Header row
        
        for item in data:
            row = []
            for key in headers:
                value = item.get(key, '')
                
                # Handle different data types
                if isinstance(value, (list, dict)):
                    # Convert complex types to JSON strings
                    row.append(json.dumps(value, ensure_ascii=False))
                elif isinstance(value, bool):
                    row.append(str(value))
                elif value is None:
                    row.append('')
                else:
                    # Convert to string and limit length (Google Sheets cell limit is ~50,000 chars)
                    str_value = str(value)
                    if len(str_value) > 45000:
                        str_value = str_value[:45000] + "...[TRUNCATED]"
                    row.append(str_value)
            
            formatted_data.append(row)
        
        return formatted_data
    
    def _auto_resize_columns(self, worksheet):
        """Auto-resize columns to fit content"""
        try:
            # This is a basic implementation - gspread doesn't have built-in auto-resize
            # We'll set reasonable column widths
            num_cols = len(worksheet.row_values(1)) if worksheet.row_count > 0 else 0
            
            if num_cols > 0:
                # Set column widths (roughly)
                body = {
                    "requests": [{
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": worksheet.id,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": num_cols
                            }
                        }
                    }]
                }
                
                self.spreadsheet.batch_update(body)
                
        except Exception as e:
            print(f"⚠️  Could not auto-resize columns: {e}")
    
    def create_analysis_sheet(self, data: List[Dict[str, Any]], analysis: Dict[str, Any], 
                            sheet_name: str = "Analysis") -> bool:
        """Create a separate sheet with data analysis"""
        if not self.client or not self.spreadsheet:
            return False
        
        try:
            # Create analysis worksheet
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=10)
            
            # Prepare analysis data
            analysis_rows = [
                ["Analysis Report", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
                ["", ""],
                ["Total Records", len(data)],
                ["", ""]
            ]
            
            # Add various analysis sections
            if "total_engagement" in analysis:
                analysis_rows.extend([
                    ["ENGAGEMENT METRICS", ""],
                    ["Total Likes", analysis["total_engagement"].get("likes", 0)],
                    ["Total Shares", analysis["total_engagement"].get("shares", 0)],
                    ["Average Likes", f"{analysis.get('average_engagement', {}).get('avg_likes', 0):.2f}"],
                    ["Average Shares", f"{analysis.get('average_engagement', {}).get('avg_shares', 0):.2f}"],
                    ["", ""]
                ])
            
            if "top_authors" in analysis:
                analysis_rows.extend([
                    ["TOP AUTHORS", "POST COUNT"],
                ])
                for author, count in analysis["top_authors"][:10]:
                    analysis_rows.append([author, count])
                analysis_rows.append(["", ""])
            
            if "sentiment_analysis" in analysis:
                sentiment = analysis["sentiment_analysis"]
                analysis_rows.extend([
                    ["SENTIMENT ANALYSIS", ""],
                    ["Positive", f"{sentiment.get('positive', 0)}%"],
                    ["Neutral", f"{sentiment.get('neutral', 0)}%"],
                    ["Negative", f"{sentiment.get('negative', 0)}%"],
                    ["", ""]
                ])
            
            if "key_topics" in analysis:
                analysis_rows.extend([
                    ["KEY TOPICS", ""],
                ])
                for topic in analysis["key_topics"]:
                    analysis_rows.append([topic, ""])
            
            # Upload analysis data
            worksheet.update('A1', analysis_rows)
            
            print(f"✅ Created analysis sheet: {sheet_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create analysis sheet: {e}")
            return False
    
    def get_spreadsheet_url(self) -> Optional[str]:
        """Get the URL of the current spreadsheet"""
        if self.spreadsheet:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
        return None
    
    def share_spreadsheet(self, email: str, role: str = "reader") -> bool:
        """Share spreadsheet with email address"""
        if not self.spreadsheet:
            return False
        
        try:
            self.spreadsheet.share(email, perm_type='user', role=role)
            print(f"✅ Shared spreadsheet with {email} as {role}")
            return True
        except Exception as e:
            print(f"❌ Failed to share spreadsheet: {e}")
            return False


def upload_to_google_sheets(data: List[Dict], config: Dict[str, Any], 
                          sheet_name: str = None, analysis: Dict[str, Any] = None) -> bool:
    """
    Convenience function to upload data to Google Sheets
    
    Args:
        data: List of dictionaries containing scraped data
        config: Configuration dictionary
        sheet_name: Name for the spreadsheet (optional)
        analysis: Analysis results to include (optional)
    
    Returns:
        bool: Success status
    """
    if not GSPREAD_AVAILABLE:
        print("❌ Google Sheets integration not available. Install dependencies first.")
        return False
    
    # Default sheet name
    if not sheet_name:
        sheet_name = f"OmniScraper_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize exporter
    exporter = GoogleSheetsExporter(config)
    
    if not exporter.client:
        print("❌ Could not initialize Google Sheets client")
        return False
    
    # Create or open spreadsheet
    spreadsheet_id = config.get("google_sheets", {}).get("spreadsheet_id")
    
    if spreadsheet_id:
        # Use existing spreadsheet
        if not exporter.open_spreadsheet(spreadsheet_id=spreadsheet_id):
            return False
    else:
        # Create new spreadsheet
        folder_id = config.get("google_sheets", {}).get("folder_id")
        if not exporter.create_spreadsheet(sheet_name, folder_id):
            return False
    
    # Export main data
    success = exporter.export_data(data, "Data")
    
    # Export analysis if provided
    if success and analysis:
        exporter.create_analysis_sheet(data, analysis, "Analysis")
    
    # Print spreadsheet URL
    url = exporter.get_spreadsheet_url()
    if url:
        print(f"📊 Spreadsheet URL: {url}")
    
    return success
