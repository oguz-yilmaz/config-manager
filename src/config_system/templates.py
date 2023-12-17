from jinja2 import Template

def render_template(template: str, variables: dict) -> str:
    t = Template(template)
    return t.render(**variables)
