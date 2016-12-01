#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/18.
# ---------------------------------
import sys
import  os
import  psutil
from _kill import  killpid

def get_pid():
    try:
        pid=open("/data/crondeamon/master/pid/crondeamon-master.pid","r").read()
        return  int(pid)
    except:
        return None
def start():
    old_pid=get_pid()
    try:
        process=psutil.Process(pid=old_pid)
    except psutil.NoSuchProcess as  e :
        process=None
        os.system("rm -rf /data/crondeamon/slave/pid/crondeamon-master.pid")
    if old_pid and process:
        cmd_line=process.cmdline()
        mask=0
        for j in cmd_line:
            if  "twistd" in j  or "crondeamon-master" in j  :
                mask+=1
        if mask>=2:
            print "server is running ! "
        else:
            os.system("mkdir -p /data/crondeamon/master/pid")
            os.system("mkdir -p /data/crondeamon/master/log")
            os.system("twistd --pidfile /data/crondeamon/master/pid/crondeamon-master.pid --logfile /data/crondeamon/master/log/crondeamon-master.log crondeamon-master")
            print "start success!"
    else:
        os.system("mkdir -p /data/crondeamon/master/pid")
        os.system("mkdir -p /data/crondeamon/master/log")
        os.system("twistd --pidfile /data/crondeamon/master/pid/crondeamon-master.pid --logfile /data/crondeamon/master/log/crondeamon-master.log crondeamon-master")
        print "start success!"
def stop():
    old_pid=get_pid()
    if old_pid:
        killpid(old_pid)
        os.system("rm -rf /data/crondeamon/master/pid/crondeamon-master.pid")
        print "stop success!"
    else:
        print "server is not running!"

if sys.argv[2]=="start":
    start()
elif sys.argv[2]=="stop":
    stop()
elif sys.argv[2]=="restart":
    stop()
    start()
