import logging
from typing import Any, Dict

from jsonschema import ValidationError, validate

logger = logging.getLogger(__name__)


def validate_config_schema(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    try:
        validate(instance=config, schema=schema)
        return True
    except ValidationError as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during schema validation: {str(e)}")
        return False


def create_schema_from_example(example: Dict[str, Any]) -> Dict[str, Any]:
    def _infer_type(value: Any) -> str:
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        return "string"

    properties = {}
    required = []

    for key, value in example.items():
        if value is not None:
            properties[key] = {"type": _infer_type(value)}
            required.append(key)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }
