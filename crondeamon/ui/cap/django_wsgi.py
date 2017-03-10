# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/9/7.
# ---------------------------------
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cap.settings")
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()