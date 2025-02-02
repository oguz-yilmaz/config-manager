#!/usr/bin/env python3
import os
from datetime import datetime

from config_system.backup import BackupManager
from config_system.storage import Storage


def backup_configs():
    """Create backup of all configurations"""
    storage = Storage()
    backup_dir = os.path.join("backups", datetime.now().strftime("%Y%m%d"))
    backup_manager = BackupManager(backup_dir)

    try:
        backup_file = backup_manager.create_backup(storage)
        print(f"Backup created successfully: {backup_file}")
    except Exception as e:
        print(f"Backup failed: {e}")


if __name__ == "__main__":
    backup_configs()
