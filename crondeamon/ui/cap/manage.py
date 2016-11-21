#!/usr/bin/env python
import os
import sys
from crondeamon.ui import cap
def get_manage_dir():
    return  cap.__path__
sys.path.append(get_manage_dir()[0])

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cap.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
