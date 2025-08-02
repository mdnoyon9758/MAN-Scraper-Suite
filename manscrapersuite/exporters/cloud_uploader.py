#!/usr/bin/env python3
"""
Cloud Uploader
Handles uploading files to Google Drive and Dropbox
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import dropbox
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class CloudUploader:
    """Cloud storage uploader for Google Drive and Dropbox"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.google_drive_service = None
        self.dropbox_client = None
        
        # Initialize cloud services if configured
        self._init_google_drive()
        self._init_dropbox()
    
    def _init_google_drive(self):
        """Initialize Google Drive API service"""
        if not self.config["cloud"]["google_drive"]["enabled"]:
            return
        
        credentials_file = self.config["cloud"]["google_drive"]["credentials_file"]
        if not credentials_file or not Path(credentials_file).exists():
            print("Google Drive credentials file not found")
            return
        
        try:
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            
            creds = None
            token_file = Path(credentials_file).parent / "token.json"
            
            # Load existing token
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.google_drive_service = build('drive', 'v3', credentials=creds)
            print("Google Drive API initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Google Drive API: {e}")
    
    def _init_dropbox(self):
        """Initialize Dropbox client"""
        if not self.config["cloud"]["dropbox"]["enabled"]:
            return
        
        access_token = self.config["cloud"]["dropbox"]["access_token"]
        if not access_token:
            print("Dropbox access token not configured")
            return
        
        try:
            self.dropbox_client = dropbox.Dropbox(access_token)
            # Test connection
            self.dropbox_client.users_get_current_account()
            print("Dropbox client initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Dropbox client: {e}")
    
    def upload_to_google_drive(self, file_path: Path, folder_id: Optional[str] = None) -> Optional[str]:
        """Upload file to Google Drive"""
        if not self.google_drive_service:
            print("Google Drive service not initialized")
            return None
        
        try:
            file_metadata = {
                'name': file_path.name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            elif self.config["cloud"]["google_drive"]["folder_id"]:
                file_metadata['parents'] = [self.config["cloud"]["google_drive"]["folder_id"]]
            
            from googleapiclient.http import MediaFileUpload
            media = MediaFileUpload(str(file_path), resumable=True)
            
            file = self.google_drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"File uploaded to Google Drive with ID: {file.get('id')}")
            return file.get('id')
            
        except Exception as e:
            print(f"Failed to upload {file_path.name} to Google Drive: {e}")
            return None
    
    def upload_to_dropbox(self, file_path: Path, dropbox_path: Optional[str] = None) -> bool:
        """Upload file to Dropbox"""
        if not self.dropbox_client:
            print("Dropbox client not initialized")
            return False
        
        try:
            if not dropbox_path:
                dropbox_path = f"/OmniScraper/{file_path.name}"
            
            with open(file_path, 'rb') as f:
                file_size = file_path.stat().st_size
                
                if file_size <= 150 * 1024 * 1024:  # 150MB
                    # Small file upload
                    self.dropbox_client.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                else:
                    # Large file upload (chunked)
                    CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks
                    
                    session_start_result = self.dropbox_client.files_upload_session_start(f.read(CHUNK_SIZE))
                    cursor = dropbox.files.UploadSessionCursor(
                        session_id=session_start_result.session_id,
                        offset=f.tell()
                    )
                    
                    while f.tell() < file_size:
                        if (file_size - f.tell()) <= CHUNK_SIZE:
                            # Last chunk
                            self.dropbox_client.files_upload_session_finish(
                                f.read(CHUNK_SIZE),
                                cursor,
                                dropbox.files.CommitInfo(path=dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                            )
                        else:
                            self.dropbox_client.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                            cursor.offset = f.tell()
            
            print(f"File uploaded to Dropbox: {dropbox_path}")
            return True
            
        except Exception as e:
            print(f"Failed to upload {file_path.name} to Dropbox: {e}")
            return False
    
    def upload_file(self, file_path: Path, destination: str = "auto") -> Dict[str, Any]:
        """Upload file to configured cloud services"""
        results = {}
        
        if destination in ("auto", "google_drive") and self.config["cloud"]["google_drive"]["enabled"]:
            google_drive_id = self.upload_to_google_drive(file_path)
            results["google_drive"] = {"success": google_drive_id is not None, "file_id": google_drive_id}
        
        if destination in ("auto", "dropbox") and self.config["cloud"]["dropbox"]["enabled"]:
            dropbox_success = self.upload_to_dropbox(file_path)
            results["dropbox"] = {"success": dropbox_success}
        
        return results
    
    def upload_multiple_files(self, file_paths: List[Path], destination: str = "auto") -> List[Dict[str, Any]]:
        """Upload multiple files to cloud services"""
        results = []
        for file_path in file_paths:
            result = self.upload_file(file_path, destination)
            result["file_path"] = str(file_path)
            results.append(result)
        return results
