from enum import Enum

from business.models.supervisor import Supervisor


def to_json(obj):
    if isinstance(obj, Supervisor):
        return ""
    elif isinstance(obj, Enum):
        return str(obj)
    else:
        return obj.__dict__

