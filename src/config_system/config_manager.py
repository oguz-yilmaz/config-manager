import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from jinja2 import Template

from .auth import AuthManager
from .models import AuditLog, ConfigVersion
from .storage import Storage, StorageError
from .validation import validate_config_schema

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(
        self,
        storage: Storage,
        auth_manager: AuthManager,
        default_schema: Optional[Dict] = None,
    ):
        self.storage = storage
        self.auth_manager = auth_manager
        self.default_schema = default_schema

    def _get_full_path(self, path: str, environment: str) -> str:
        return f"{environment}/{path}"

    def get_config(self, path: str, environment: str = "prod") -> Optional[Dict]:
        try:
            full_path = self._get_full_path(path, environment)
            config = self.storage.get_config(full_path)

            if not config:
                return None

            # Apply template substitution
            template = Template(json.dumps(config.data))
            rendered = template.render(env=environment)

            return json.loads(rendered)

        except Exception as e:
            logger.error(f"Error getting config {path}: {str(e)}")
            raise

    def update_config(
        self,
        path: str,
        config_data: Dict,
        user: str,
        environment: str = "prod",
        schema: Optional[Dict] = None,
        comment: Optional[str] = None,
    ) -> None:
        try:
            # Validate schema if provided
            validate_schema = schema or self.default_schema
            if validate_schema and not validate_config_schema(
                config_data, validate_schema
            ):
                raise ValueError("Configuration does not match schema")

            # Create new version of the configuration
            version = ConfigVersion(
                version=datetime.utcnow().isoformat(), data=config_data, comment=comment
            )

            full_path = self._get_full_path(path, environment)

            # Store current version
            self.storage.put_config(full_path, version)

            # Store in version history
            self.storage.put_config(f"versions/{full_path}/{version.version}", version)

            log = AuditLog(
                action="update",
                path=full_path,
                user=user,
                details={"version": version.version, "comment": comment},
            )
            self.storage.add_audit_log(log)
        except Exception as e:
            logger.error(f"Error updating config {path}: {str(e)}")
            raise

    def rollback(
        self, path: str, version: str, user: str, environment: str = "prod"
    ) -> None:
        try:
            full_path = self._get_full_path(path, environment)

            # Get specific version
            target_version = self.storage.get_config(f"versions/{full_path}/{version}")
            if not target_version:
                raise ValueError(f"Version {version} not found")

            # Update current version
            self.storage.put_config(path, target_version)

            # Add audit log
            log = AuditLog(
                action="rollback",
                path=full_path,
                user=user,
                details={"version": version},
            )
            self.storage.add_audit_log(log)
        except Exception as e:
            logger.error(f"Error rolling back {path} to {version}: {str(e)}")
            raise

    def get_versions(self, path: str, environment: str = "prod") -> List[ConfigVersion]:
        full_path = self._get_full_path(path, environment)

        return self.storage.get_versions(full_path)

    def verify_api_key(
        self, api_key: str, required_roles: Optional[List[str]] = None
    ) -> bool:
        return self.auth_manager.verify_api_key(api_key, required_roles)
