import logging
from typing import Any, Dict

from jinja2 import BaseLoader, Environment, Template

logger = logging.getLogger(__name__)


class TemplateRenderer:
    def __init__(self):
        self.env = Environment(loader=BaseLoader(), autoescape=True)

    def render(self, template_str: str, variables: Dict[str, Any]) -> str:
        try:
            template = self.env.from_string(template_str)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise ValueError(f"Failed to render template: {str(e)}")

    def validate_template(self, template_str: str) -> bool:
        try:
            self.env.from_string(template_str)
            return True
        except Exception:
            return False
