# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/25.
# ---------------------------------
import  psutil
import  sys
def killpid(pid):
    try:
        try:
            pid=int(pid)
            _mainprocess=psutil.Process(pid)
            _main_cmd=_mainprocess.cmdline()
            _mark=0
            for i in _main_cmd:
                if "twistd" in i :
                    _mark+=1
                if "crondeamon" in i:
                    _mark+=1

            if _mark>=3 and _mainprocess.is_running():
                childpids=_mainprocess.children(True)
                buff=dict([(k.pid,k.create_time()) for k in childpids])
                _mainprocess.send_signal(9)
                for j in childpids:
                    try:
                        _process=psutil.Process(j.pid)
                    except:
                        pass
                    else:
                        if _process.is_running()  and j.create_time()==buff[j.pid] :
                            _process.send_signal(9)
        except:
            pass
        else:
            print "PID: %s have been killed!"%pid
    except Exception as e :
        print e.message
    return True
