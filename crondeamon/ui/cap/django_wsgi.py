# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/9/7.
# ---------------------------------
import os
import sys
import psutil
if sys.argv.__len__()>=3 and sys.argv[1]=="stopuwsgi":
    one_pidobj=psutil.Process(pid=1)
    one_pidobj.username()
    one_pidobj.cmdline()
    subprocesslist=one_pidobj.children(True)
    for i in subprocesslist:
        try:
            if i.is_running() and i.username()=="cap":
                try:
                    cmdline=i.cmdline()
                    if len(cmdline)>=3:
                        if "-x" == cmdline[-2] and sys.argv[2]  ==cmdline[-1]:
                            i.send_signal(9)
                except:
                    pass
        except:
            pass
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cap.settings")
    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()