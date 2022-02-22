import json
import os
import tempfile
from enum import Enum
import datetime

from business.models.supervisor import Supervisor


def to_json(obj):
    if isinstance(obj, Supervisor):
        return ""
    elif isinstance(obj, Enum) or isinstance(obj, datetime.date):
        return str(obj)
    else:
        return obj.__dict__


def generate_temp_json_file(content):
    temp_dir_path = tempfile.mkdtemp()
    temp_file = open(os.path.join(temp_dir_path, 'result.json'), "w+")
    temp_file.write(json.dumps(content, default=to_json, indent=4))
    temp_file.close()
    return temp_file


def compare_file_error_msg(expected, result):
    return f"\nContent of files are not the same \n Expected : {expected.name} \n Result : {result.name}"
