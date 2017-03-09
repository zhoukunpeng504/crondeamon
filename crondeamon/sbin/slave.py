#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/18.
# ---------------------------------
import sys
import  os
import  psutil
from _kill import  killpid
import  ConfigParser

cfg=ConfigParser.ConfigParser()
result=cfg.read("/etc/crondeamon.ini")
assert  result==["/etc/crondeamon.ini"]
assert cfg.sections()==["crondeamon"]
config=dict(cfg.items("crondeamon"))
datadir=config["datadir"]
slave_dir=os.path.join(datadir,"slave")

def get_pid():
    try:
        pid=open(os.path.join(datadir,"/slave/pid/crondeamon-slave.pid"),"r").read()
        return  int(pid)
    except:
        return None
def start():
    old_pid=get_pid()
    try:
        process=psutil.Process(pid=old_pid)
    except psutil.NoSuchProcess as  e :
        process=None
        os.system("rm -rf %s/pid/crondeamon-slave.pid"%slave_dir)
    if old_pid and process:
        cmd_line=process.cmdline()
        mask=0
        for j in cmd_line:
            if  "twistd" in j  or "crondeamon-slave" in j  :
                mask+=1
        if mask>=2:
            print "server is running ! "
        else:
            os.system("mkdir -p %s/pid"%slave_dir)
            os.system("mkdir -p %s/log"%slave_dir)
            os.system("twistd --pidfile %s/pid/crondeamon-slave.pid --logfile %s/log/crondeamon-slave.log crondeamon-slave"%(slave_dir,slave_dir))
            print "start success!"
    else:
        os.system("mkdir -p %s/pid"%slave_dir)
        os.system("mkdir -p %s/log"%slave_dir)
        os.system("twistd --pidfile %s/pid/crondeamon-slave.pid --logfile %s/log/crondeamon-slave.log crondeamon-slave"%(slave_dir,slave_dir))
        print "start success!"
def stop():
    old_pid=get_pid()
    if old_pid:
        killpid(old_pid)
        os.system("rm -rf  %s/pid/crondeamon-slave.pid"%slave_dir)
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
