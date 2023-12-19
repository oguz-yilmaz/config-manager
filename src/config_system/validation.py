from jsonschema import validate, ValidationError

def validate_config_schema(config: dict, schema: dict) -> bool:
    try:
        validate(instance=config, schema=schema)
        return True
    except ValidationError:
        return False
