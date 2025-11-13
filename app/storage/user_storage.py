import csv
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import threading
import logging

from app.config import get_settings
from app.storage.google_sheets import get_sheets_storage

settings = get_settings()
logger = logging.getLogger(__name__)


class UserStorage:
    COLUMNS = [
        'user_id', 'created_at', 'updated_at',
        'discord_id', 'discord_username',
        'telegram_id', 'telegram_username'
    ]

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.csv"
        self.lock = threading.Lock()
        self.sheets = get_sheets_storage()
        self._init_file()

    def _init_file(self):
        if not self.users_file.exists():
            try:
                with open(self.users_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.COLUMNS)
                logger.info(f"Initialized CSV file: {self.users_file}")
            except Exception as e:
                logger.error(f"Failed to initialize CSV file: {e}")
                raise

    def _safe_write_csv(self, rows: List[Dict]):
        try:
            temp_fd, temp_path = tempfile.mkstemp(dir=self.data_dir, suffix='.tmp')
            try:
                with os.fdopen(temp_fd, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
                    writer.writeheader()
                    writer.writerows(rows)
                shutil.move(temp_path, self.users_file)
                logger.debug(f"Successfully wrote {len(rows)} rows to CSV")
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
        except Exception as e:
            logger.error(f"Failed to write CSV file: {e}")
            raise

    def _get_next_user_id(self) -> int:
        try:
            with open(self.users_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    return 1
                return max(int(row['user_id']) for row in rows) + 1
        except Exception as e:
            logger.error(f"Failed to get next user ID: {e}")
            return 1

    def _row_to_user(self, row: Dict) -> Dict:
        return {
            'id': int(row['user_id']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'discord': {
                'id': row['discord_id'],
                'username': row['discord_username'],
                'bound': bool(row['discord_id'])
            } if row['discord_id'] else None,
            'telegram': {
                'id': row['telegram_id'],
                'username': row['telegram_username'],
                'bound': bool(row['telegram_id'])
            } if row['telegram_id'] else None
        }

    def create_user(self) -> Dict:
        with self.lock:
            user_id = self._get_next_user_id()
            now = datetime.utcnow().isoformat()

            row = {col: '' for col in self.COLUMNS}
            row['user_id'] = user_id
            row['created_at'] = now
            row['updated_at'] = now

            with open(self.users_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
                writer.writerow(row)

            self.sheets.sync_row(row, self.COLUMNS)

            return {
                'id': user_id,
                'created_at': now,
                'updated_at': now,
                'discord': None,
                'telegram': None
            }

    def get_user(self, user_id: int) -> Optional[Dict]:
        with self.lock:
            with open(self.users_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['user_id']) == user_id:
                        return self._row_to_user(row)
        return None

    def get_user_by_platform(self, platform: str, platform_user_id: str) -> Optional[Dict]:
        with self.lock:
            with open(self.users_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row[f'{platform}_id'] == platform_user_id:
                        return self._row_to_user(row)
        return None

    def bind_platform(self, user_id: int, platform: str,
                      platform_user_id: str, username: Optional[str] = None) -> Dict:
        with self.lock:
            rows = []
            updated_user = None
            user_found = False
            now = datetime.utcnow().isoformat()

            try:
                with open(self.users_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_platform_id = row.get(f'{platform}_id', '')
                        if existing_platform_id and existing_platform_id == platform_user_id:
                            if int(row['user_id']) != user_id:
                                logger.warning(
                                    f"Attempted duplicate binding: {platform} ID {platform_user_id} "
                                    f"already bound to user {row['user_id']}"
                                )
                                platform_name = platform.capitalize()
                                raise ValueError(
                                    f"This {platform_name} account is already connected. Please use a different {platform_name} account or contact support."
                                )
            except FileNotFoundError:
                logger.error("CSV file not found during duplicate check")
                raise

            try:
                with open(self.users_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if int(row['user_id']) == user_id:
                            user_found = True
                            row[f'{platform}_id'] = platform_user_id
                            row[f'{platform}_username'] = username or ''
                            row['updated_at'] = now
                            updated_user = self._row_to_user(row)
                        rows.append(row)

                if not user_found:
                    logger.error(f"User {user_id} not found for platform binding")
                    raise ValueError(f"User {user_id} not found")

                self._safe_write_csv(rows)
                logger.info(f"Successfully bound {platform} ID {platform_user_id} to user {user_id}")

                for row in rows:
                    if int(row['user_id']) == user_id:
                        self.sheets.sync_row(row, self.COLUMNS)
                        break

                return updated_user
            except Exception as e:
                logger.error(f"Failed to bind platform: {e}")
                raise

    def unbind_platform(self, user_id: int, platform: str) -> Optional[Dict]:
        with self.lock:
            rows = []
            updated_user = None
            now = datetime.utcnow().isoformat()

            try:
                with open(self.users_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if int(row['user_id']) == user_id:
                            row[f'{platform}_id'] = ''
                            row[f'{platform}_username'] = ''
                            row['updated_at'] = now
                            updated_user = self._row_to_user(row)
                        rows.append(row)

                self._safe_write_csv(rows)
                logger.info(f"Successfully unbound {platform} from user {user_id}")

                return updated_user
            except Exception as e:
                logger.error(f"Failed to unbind platform: {e}")
                raise

    def get_all_users(self) -> List[Dict]:
        with self.lock:
            users = []
            with open(self.users_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    users.append(self._row_to_user(row))
            return users


_storage_instance = None


def get_user_storage() -> UserStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = UserStorage(settings.CSV_DATA_DIR)
    return _storage_instance
