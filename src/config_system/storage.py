import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

import etcd3

from .models import AuditLog, ConfigVersion

logger = logging.getLogger(__name__)


class StorageError(Exception):
    pass


class Storage:
    def __init__(
        self, host: str = "localhost", port: int = 2379, audit_db: str = "audit.db"
    ):
        self.etcd = etcd3.client(host=host, port=port)
        self.audit_db = audit_db
        self._init_audit_db()

    def _init_audit_db(self):
        try:
            with sqlite3.connect(self.audit_db) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY,
                        action TEXT NOT NULL,
                        path TEXT NOT NULL,
                        user TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        details TEXT
                    )
                """
                )
        except Exception as e:
            logger.error(f"Failed to initialize audit database: {str(e)}")
            raise StorageError("Failed to initialize storage")

    def get_config(self, path: str) -> Optional[ConfigVersion]:
        try:
            value = self.etcd.get(f"/config/{path}")
            return ConfigVersion.parse_raw(value[0]) if value[0] else None
        except Exception as e:
            logger.error(f"Error retrieving config {path}: {str(e)}")
            raise StorageError(f"Failed to get config: {str(e)}")

    def put_config(self, path: str, version: ConfigVersion):
        try:
            self.etcd.put(f"/config/{path}", version.json())
        except Exception as e:
            logger.error(f"Error storing config {path}: {str(e)}")
            raise StorageError(f"Failed to store config: {str(e)}")

    def get_versions(self, path: str) -> List[ConfigVersion]:
        try:
            versions = []
            kvs = self.etcd.get_prefix(f"/versions/{path}/")
            for kv in kvs:
                versions.append(ConfigVersion.parse_raw(kv[0]))
            return sorted(versions, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            logger.error(f"Error retrieving versions for {path}: {str(e)}")
            raise StorageError(f"Failed to get versions: {str(e)}")

    def add_audit_log(self, log: AuditLog):
        try:
            with sqlite3.connect(self.audit_db) as conn:
                conn.execute(
                    """
                    INSERT INTO audit_log 
                    (action, path, user, timestamp, details)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        log.action,
                        log.path,
                        log.user,
                        log.timestamp.isoformat(),
                        json.dumps(log.details),
                    ),
                )
        except Exception as e:
            logger.error(f"Error adding audit log: {str(e)}")
            raise StorageError(f"Failed to add audit log: {str(e)}")

    def get_audit_logs(
        self,
        path: Optional[str] = None,
        user: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        try:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []

            if path:
                query += " AND path = ?"
                params.append(path)
            if user:
                query += " AND user = ?"
                params.append(user)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            with sqlite3.connect(self.audit_db) as conn:
                cursor = conn.execute(query, params)
                return [
                    AuditLog(
                        id=row[0],
                        action=row[1],
                        path=row[2],
                        user=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        details=json.loads(row[5]) if row[5] else {},
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {str(e)}")
            raise StorageError(f"Failed to get audit logs: {str(e)}")

    def ping(self) -> bool:
        try:
            self.etcd.get("health_check")
            return True
        except Exception:
            return False

    def dump_all(self) -> Dict:
        try:
            result = {}
            kvs = self.etcd.get_all()
            for kv in kvs:
                result[kv[1].key.decode()] = kv[0].decode()
            return result
        except Exception as e:
            logger.error(f"Error dumping all configs: {str(e)}")
            raise StorageError(f"Failed to dump configs: {str(e)}")

    def restore_from_backup(self, backup_data: Dict):
        try:
            with self.etcd.transaction() as txn:
                for key, value in backup_data.items():
                    txn.put(key, value)
        except Exception as e:
            logger.error(f"Error restoring from backup: {str(e)}")
            raise StorageError(f"Failed to restore from backup: {str(e)}")
