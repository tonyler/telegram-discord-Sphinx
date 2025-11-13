"""Google Sheets storage backend"""
import gspread
import logging
from google.oauth2.service_account import Credentials
from typing import Dict, List, Optional
from pathlib import Path
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class GoogleSheetsStorage:
    """Google Sheets storage for real-time online backup"""

    def __init__(self):
        self.enabled = settings.GOOGLE_SHEETS_ENABLED
        self.client = None
        self.worksheet = None

        if self.enabled:
            try:
                self._initialize()
                logger.info("Google Sheets storage initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Sheets: {e}")
                self.enabled = False

    def _initialize(self):
        """Initialize Google Sheets client"""
        if not settings.GOOGLE_SERVICE_ACCOUNT_FILE:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE not configured")

        if not settings.GOOGLE_SHEETS_ID:
            raise ValueError("GOOGLE_SHEETS_ID not configured")

        # Load credentials
        creds_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_FILE)
        if not creds_path.exists():
            raise FileNotFoundError(f"Service account file not found: {creds_path}")

        credentials = Credentials.from_service_account_file(
            str(creds_path),
            scopes=SCOPES
        )

        # Initialize client
        self.client = gspread.authorize(credentials)
        
        # Open spreadsheet
        spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEETS_ID)
        
        # Get or create worksheet
        try:
            self.worksheet = spreadsheet.worksheet("Users")
        except gspread.exceptions.WorksheetNotFound:
            self.worksheet = spreadsheet.add_worksheet(title="Users", rows=1000, cols=20)
            logger.info("Created new 'Users' worksheet")

    def _ensure_headers(self, columns: List[str]):
        """Ensure worksheet has proper headers"""
        if not self.enabled or not self.worksheet:
            return

        try:
            # Check if headers exist
            existing_headers = self.worksheet.row_values(1)
            
            if not existing_headers or existing_headers != columns:
                # Set headers
                self.worksheet.update('A1', [columns])
                logger.info("Updated worksheet headers")
        except Exception as e:
            logger.error(f"Failed to set headers: {e}")

    def sync_row(self, row_data: Dict, columns: List[str]):
        """
        Sync a single row to Google Sheets
        
        Args:
            row_data: Dict with row data
            columns: List of column names
        """
        if not self.enabled or not self.worksheet:
            return

        try:
            # Ensure headers are set
            self._ensure_headers(columns)

            # Convert row dict to list in column order
            values = [row_data.get(col, '') for col in columns]
            user_id = row_data.get('user_id', '')

            if not user_id:
                logger.warning("Cannot sync row without user_id")
                return

            # Find existing row by user_id
            try:
                cell = self.worksheet.find(str(user_id), in_column=1)
                if cell:
                    row_num = cell.row
                    # Update existing row
                    self.worksheet.update(f'A{row_num}', [values])
                    logger.debug(f"Updated row {row_num} for user {user_id}")
                else:
                    # Append new row if not found
                    self.worksheet.append_row(values)
                    logger.debug(f"Appended new row for user {user_id}")
            except Exception as e:
                # If cell not found or any other error, append new row
                logger.debug(f"Cell not found or error searching, appending new row: {e}")
                self.worksheet.append_row(values)
                logger.debug(f"Appended new row for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to sync row to Google Sheets: {e}")
            # Don't raise - we don't want Google Sheets failures to break the app

    def sync_all_rows(self, rows: List[Dict], columns: List[str]):
        """
        Sync all rows to Google Sheets (bulk operation)
        
        Args:
            rows: List of row dicts
            columns: List of column names
        """
        if not self.enabled or not self.worksheet:
            logger.info("Google Sheets not enabled, skipping sync")
            return

        try:
            logger.info(f"Syncing {len(rows)} rows to Google Sheets...")

            # Clear existing data
            self.worksheet.clear()

            # Prepare data with headers
            sheet_data = [columns]
            for row in rows:
                values = [row.get(col, '') for col in columns]
                sheet_data.append(values)

            # Bulk update
            self.worksheet.update('A1', sheet_data)
            
            logger.info(f"Successfully synced {len(rows)} rows to Google Sheets")

        except Exception as e:
            logger.error(f"Failed to bulk sync to Google Sheets: {e}")
            # Don't raise - we don't want Google Sheets failures to break the app

    def delete_row(self, user_id: int):
        """Delete a row by user_id"""
        if not self.enabled or not self.worksheet:
            return

        try:
            cell = self.worksheet.find(str(user_id), in_column=1)
            if cell:
                self.worksheet.delete_rows(cell.row)
                logger.debug(f"Deleted row for user {user_id}")
            else:
                logger.debug(f"Row for user {user_id} not found in sheet")
        except Exception as e:
            logger.error(f"Failed to delete row from Google Sheets: {e}")


# Singleton instance
_sheets_instance = None


def get_sheets_storage() -> GoogleSheetsStorage:
    """Get singleton Google Sheets storage instance"""
    global _sheets_instance
    if _sheets_instance is None:
        _sheets_instance = GoogleSheetsStorage()
    return _sheets_instance
