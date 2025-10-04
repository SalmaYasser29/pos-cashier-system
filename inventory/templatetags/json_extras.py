import json
from django import template

register = template.Library()

@register.filter
def json_to_dict(value):
    """
    Convert a JSON string into a Python dict for templates.
    """
    if not value:
        return {}
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return {}
