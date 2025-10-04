# inventory/utils.py
import json
from django.forms.models import model_to_dict
from django.utils.timezone import now
from .models import ActivityLog


def log_action(user, action, instance, old_instance=None):
    """
    Create an activity log entry whenever a model instance is created, updated, or deleted.
    - For create: only new_data is stored.
    - For update: only changed fields are stored in old_data/new_data.
    - For delete: only old_data is stored.
    """

    old_data, new_data = {}, {}

    # Handle updates
    if action == "update" and old_instance:
        old_dict = model_to_dict(old_instance)
        new_dict = model_to_dict(instance)

        for field, old_value in old_dict.items():
            new_value = new_dict.get(field)
            if str(old_value) != str(new_value):  
                old_data[field] = str(old_value)
                new_data[field] = str(new_value)

    # Handle creates
    elif action == "create":
        new_data = {k: str(v) for k, v in model_to_dict(instance).items()}

    # Handle deletes
    elif action == "delete" and old_instance:
        old_data = {k: str(v) for k, v in model_to_dict(old_instance).items()}

    ActivityLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        model=instance.__class__.__name__,
        object_id=instance.pk or 0,
        object_repr=str(instance),
        branch=getattr(instance, "branch", None),
        timestamp=now(),
        old_data=json.dumps(old_data, ensure_ascii=False) if old_data else None,
        new_data=json.dumps(new_data, ensure_ascii=False) if new_data else None,
    )


def get_changes(log):
    """
    Compare old_data and new_data JSON and return only changed fields.
    Returns a list of dicts: [{field, old, new}, ...]
    """

    try:
        old = json.loads(log.old_data or "{}")
    except json.JSONDecodeError:
        old = {}

    try:
        new = json.loads(log.new_data or "{}")
    except json.JSONDecodeError:
        new = {}

    changes = []

    for key in set(old.keys()) | set(new.keys()):
        old_val = old.get(key)
        new_val = new.get(key)
        if old_val != new_val:  
            changes.append({
                "field": key,
                "old": old_val,
                "new": new_val
            })

    return changes
