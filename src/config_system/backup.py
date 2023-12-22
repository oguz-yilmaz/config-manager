import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, backup_dir: str, retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days

    def create_backup(self, storage) -> Optional[Path]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.json"

            with backup_file.open("w") as f:
                json.dump(storage.dump_all(), f, indent=2)

            self._cleanup_old_backups()
            return backup_file
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return None

    def restore_backup(self, storage, backup_file: Path) -> bool:
        try:
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            with backup_file.open("r") as f:
                data = json.load(f)

            storage.restore_from_backup(data)
            return True
        except Exception as e:
            logger.error(f"Backup restoration failed: {str(e)}")
            return False

    def _cleanup_old_backups(self):
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for backup_file in self.backup_dir.glob("config_backup_*.json"):
            try:
                file_date = datetime.strptime(backup_file.stem[13:], "%Y%m%d_%H%M%S")
                if file_date < cutoff_date:
                    backup_file.unlink()
            except Exception as e:
                logger.warning(f"Error cleaning up backup {backup_file}: {str(e)}")
