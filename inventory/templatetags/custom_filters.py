# inventory/templatetags/custom_filters.py
import json
import ast
from django import template

register = template.Library()

@register.filter
def json_to_dict(value):
    """Safely convert JSON or Python dict string to dict"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            # fallback for old logs with single quotes
            return ast.literal_eval(value)
        except Exception:
            return {}
