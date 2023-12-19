import pytest
from config_system.templates import render_template

def test_simple_template():
    template = "Hello {{ name }}"
    assert render_template(template, {"name": "World"}) == "Hello World"
