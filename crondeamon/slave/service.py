# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/4.
# ---------------------------------
from twisted.web import  xmlrpc
from twisted.internet import  reactor,task,defer,threads
from twisted.enterprise import  adbapi
from txscheduling.cron import CronSchedule
from txscheduling.task import  ScheduledCall
from twisted.internet import  protocol
import  MySQLdb
import psutil
import  sys

reactor.suggestThreadPoolSize(500)   #线程池改为500， 防止线程占满
reload(sys)
sys.setdefaultencoding("utf-8")
import  socket
MYSQLCONFIG={}
RID_BUFF={}                       #CRON 专用全局变量
RID_BUFF_TASK={}                  #TASK 专用全局变量
PID_BUFF={}

def int_to_hexstring(intvalue):
    result=hex(intvalue)
    result=result.strip("L")
    result=result.strip("0x")
    return  result


@defer.inlineCallbacks
def run_conn_fun(fun,*args):
    try:
        global conn
        result=yield  getattr(conn,fun)(*args)
    except (MySQLdb.OperationalError,adbapi.ConnectionLost):
        try:
            conn.close()
        except:
            pass
        conn=adbapi.ConnectionPool("MySQLdb",host=MYSQLCONFIG["host"],user=MYSQLCONFIG["user"],passwd=MYSQLCONFIG["passwd"],charset=MYSQLCONFIG["charset"],port=MYSQLCONFIG["port"],db=MYSQLCONFIG["db"],cp_reconnect=True)
        result=yield  getattr(conn,fun)(*args)
    defer.returnValue(result)

def set_time_out(seconds,deferjob):
    "给一个deferjob添加一个超时时间,防止一个xmlrpc运行时间过长。"
    def _handle(deferjob):
        if deferjob.called:
            pass
        else:
            deferjob.cancel()
    seconds=int(seconds)
    reactor.callLater(seconds,_handle,deferjob)
    return  True

class SubRpc(xmlrpc.XMLRPC):
    def xmlrpc_test(self):
        return "test"
    @defer.inlineCallbacks
    def xmlrpc_init(self,tid,svnpath,svnversion,svnuser,svnpasswd,mode="cron"):
        '''初始化task
        参数说明：
        tid  int
        返回True 代表已初始化
        返回False 代表启动初始化失败'''
        tid=int(tid)

        def _init():
            print "begin init"
            if mode=="cron":
                run_conn_fun("runOperation","update   cron_task set status=2 WHERE  tid=%s",(tid,))   #正在部署
            else:
                run_conn_fun("runOperation","update   task_task set status=2 WHERE  tid=%s",(tid,))   #正在部署
            print "begin mkdir"
            dirname="%s"%(tid)
            dirname=dirname.encode("utf-8")
            if mode=="cron":
                pass
            else:
                dirname="task/"+dirname
            real_dir=os.path.join(datadir,dirname)
            containname=svnpath.strip("/").split("/")[-1]
            version=svnversion
            mkdircommand=("mkdir -p %s"%real_dir)
            rmcommand=("rm  %s/* -rf"%real_dir)
            print mkdircommand,  rmcommand
            result=os.system(mkdircommand)
            os.system(rmcommand)
            print "result",result
            assert  result==0
            print "begin check"
            command="cd %s && svn checkout  -r %s  %s  --username %s --password %s --no-auth-cache --non-interactive"%(real_dir,version,svnpath,svnuser,svnpasswd)
            customcommand="cd %s && cd %s && %s"%(real_dir,containname,"pwd")
            print command
            print "end init"
            assert  result==0
            assert os.system(command)==0
            assert os.system(customcommand)==0
        try:
            yield threads.deferToThread(_init)
        except Exception as e :
            print e
            if mode=="cron":
                yield run_conn_fun("runOperation" ,"update   cron_task set status=3 WHERE  tid=%s",(tid,))
            else:
                yield run_conn_fun("runOperation","update   task_task set status=3 WHERE  tid=%s",(tid,))
            result=False
        else:
            if mode=="cron":
                yield run_conn_fun("runOperation","update   cron_task set status=1 WHERE  tid=%s",(tid,))
            else:
                yield run_conn_fun("runOperation","update   task_task set status=1 WHERE  tid=%s",(tid,))

            result=True
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_run(self,tid,rid,args,mode="cron"):
        "运行task "
        yield self.xmlrpc_stop(tid,mode)
        class SubProcessProtocol(protocol.ProcessProtocol):
            @defer.inlineCallbacks
            def connectionMade(self):
                print "connectionMade! tid:%s"%tid
                global  RID_BUFF
                global RID_BUFF_TASK
                self.stdout=''
                self.stderr=''
                if mode=="cron":
                    RID_BUFF[(tid,rid)]=self.transport
                    try:
                        yield run_conn_fun("runOperation","update   cron_runlog  set status =1 , begintime=UNIX_TIMESTAMP() WHERE rid=%s",(rid,))
                    except:
                        pass
                else:
                    RID_BUFF_TASK[(tid,rid)]=self.transport
                    try:
                        yield run_conn_fun("runOperation","update   task_runlog  set status =1 , begintime=UNIX_TIMESTAMP() WHERE rid=%s",(rid,))
                    except:
                        pass
            def outReceived(self, data):
                def stringhandle(_str):
                    try:
                        result=_str.decode("utf-8")
                        return  result
                    except:
                        pass
                    try:
                        result=_str.decode("gbk")
                        return  result
                    except:
                        pass
                    try:
                        result=str([_str])
                        return  result
                    except:
                        pass
                    return  u"UTF-8  GBK  均无法正常解码。 无法正常获取！ 请更换编码！"
                if  not  isinstance(data,unicode):
                    data=stringhandle(data)
                if hasattr(self,"stdout"):
                    self.stdout+=data
                else:
                    self.stdout=data
                self.stdout=self.stdout[-1000:]
            def errReceived(self, data):
                if hasattr(self,"stderr"):
                    self.stderr+=data
                else:
                    self.stderr=data
                self.stderr=self.stderr[-1000:]
            def inConnectionLost(self):
                pass
            def outConnectionLost(self):
                pass
            def errConnectionLost(self):
                pass
            @defer.inlineCallbacks
            def processExited(self, reason):
                print "processExited!"
                global  RID_BUFF
                global  RID_BUFF_TASK
                returnvalue=reason.value.exitCode
                delay=task.deferLater(reactor,2,lambda i:i,123)
                yield  delay
                if mode=="cron":
                    if RID_BUFF.has_key((tid,rid)):
                        del RID_BUFF[(tid,rid)]
                    print self.stdout
                    print self.stderr
                    try:
                        yield run_conn_fun("runOperation","update   cron_runlog set status=%s ,stdout = %s ,stderror=%s,endtime=UNIX_TIMESTAMP()  WHERE  rid=%s",(3 if returnvalue !=0 else 2,self.stdout,
                                       self.stderr,rid))
                    except:
                        pass
                else:
                    if RID_BUFF_TASK.has_key((tid,rid)):
                        del RID_BUFF_TASK[(tid,rid)]
                    print self.stdout
                    print self.stderr
                    try:
                        yield run_conn_fun("runOperation","update   task_runlog set status=%s ,stdout = %s ,stderror=%s,endtime=UNIX_TIMESTAMP()  WHERE  rid=%s",(3 if returnvalue!=0 else 2,self.stdout,
                                       self.stderr,rid))
                    except:
                        pass
            def processEnded(self, reason):
                pass
        p=SubProcessProtocol()
        tid=int(tid)
        taskinfo= yield run_conn_fun("runQuery","select svnpath,filename from    %s  WHERE  tid=%%s"%("cron_task" if mode=="cron" else "task_task",),(tid,))
        svnpath,filename=taskinfo[0]
        filename_path="%s/%s"%(tid,svnpath.strip("/").split("/")[-1])
        filename_path=filename_path.encode("utf-8")
        print filename_path
        argument=[_ for _ in filename.strip().split(" ") if _ != ""]
        if mode=="cron":
            filename_path=os.path.join(datadir,filename_path)
        else:
            filename_path=os.path.join(datadir,"task",filename_path)
        argument=map(lambda i:i.encode("utf-8") ,argument)
        print "argument:",argument
        reactor.spawnProcess(p,argument[0],argument,env=os.environ,path=filename_path)
        defer.returnValue(True)

    def xmlrpc_stop(self,tid,mode="cron"):
        "停止一个tid的所有任务"
        if mode=="cron":
            global  RID_BUFF
            keys=RID_BUFF.keys()
            for i in keys:
                if tid == i[0] :
                    pid=RID_BUFF[i].pid
                    _mainprocess=psutil.Process(pid)
                    childpids=_mainprocess.children(True)
                    buff=dict([(k.pid,k.create_time()) for k in childpids])
                    print buff
                    RID_BUFF[i].signalProcess(9)
                    for j in childpids:
                        try:
                            _process=psutil.Process(j.pid)
                        except:
                            pass
                        else:
                            if _process.is_running()  and j.create_time()==buff[j.pid] :
                                _process.send_signal(9)
                    del RID_BUFF[i]
        else:
            global  RID_BUFF_TASK
            keys=RID_BUFF_TASK.keys()
            for i in keys:
                if tid == i[0]:
                    pid=RID_BUFF_TASK[i].pid
                    _mainprocess=psutil.Process(pid)
                    childpids=_mainprocess.children(True)
                    buff=dict([(k.pid,k.create_time()) for k in childpids])
                    print buff
                    RID_BUFF_TASK[i].signalProcess(9)
                    for j in childpids:
                        try:
                            _process=psutil.Process(j.pid)
                        except:
                            pass
                        else:
                            if _process.is_running()  and j.create_time()==buff[j.pid] :
                                _process.send_signal(9)
                    del RID_BUFF_TASK[i]
        return True
    def xmlrpc_getstatus(self,tid,mode="cron"):
        "查看一个task是否正在运行。True 正在运行  False 不在运行"
        global  RID_BUFF
        global  RID_BUFF_TASK
        print "RID_BUFF_TASK",RID_BUFF_TASK
        if mode=="cron":
            keys=RID_BUFF.keys()
            for i in  keys:
                if tid==i[0]:
                    result=True
                    break
            else:
                result= False
        else:
            keys=RID_BUFF_TASK.keys()
            for i in  keys:
                if tid==i[0]:
                    result=True
                    break
            else:
                result=False
        return  result


class Valid(object):

    def valid_ip(self,ip):
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False

    def valid_cronrule(self,rule):
        rule=rule.strip()
        try:
            CronSchedule(rule)
        except:
            return (False,"时间规则不符合要求")
        else:
            return True

    def valid_cronadd(self,name,rule,svnpath,version,svnuser,svnpasswd,info,args,filename):
        "cronadd 是的参数验证"
        args=locals()
        _config={"rule":"时间规则","svnpath":"SVN url","svnuser":"svn user","svnpasswd":"svn passwd","info":"功能描述",
                 "project":"所属应用-项目","app":"所属应用-应用","name":"名称","args":"运行参数","filename":"执行文件名"}
        for i in args:
            if i in ("rule","svnpath","svnuser","svnpasswd","info","project","app","name"):
                if args[i]=='':
                    return False,"{0}不能为空".format(_config[i])
                if i=="rule":
                    if  self.valid_cronrule(args[i])!=True:
                        return self.valid_cronrule(args[i])
            elif i in ("version",):
                try :
                    int(args[i])
                except:
                    return False,"svn版本不合法！"
            elif i =="args":
                if len(args[i])>0 :
                    if args[i][0]==" ":
                        return False,"运行参数首位不能为空格"
                    if args[i][-1]==" ":
                        return  False,"运行参数尾部不能为空格"
                    if "  " in args[i]:
                        return  False,"运行参数中间以单个空格分隔！"
            elif i=="filename":
                if len(args[i])==0 or args[i].strip()=="":
                    return  False,"执行命令不能为空"
        return True

    def valid_deaadd(self,name,svnpath,version,svnuser,svnpasswd,info,args,filename):
        "daeman process 的参数验证"
        args=locals()
        _config={"rule":"时间规则","svnpath":"SVN url","svnuser":"svn user","svnpasswd":"svn passwd","info":"功能描述",
                 "project":"所属应用-项目","app":"所属应用-应用","name":"名称"}
        for i in args:
            if i in ("svnpath","svnuser","svnpasswd","info","project","app","name"):
                if args[i]=='':
                    return False,"{0}不能为空".format(_config[i])
            elif i in ("version",):
                try :
                    int(args[i])
                except:
                    return False,"svn版本不合法！"
            elif i =="ip":
                if self.valid_ip(args[i])==False:
                    return False,"IP非法！"
            elif i =="args":
                if len(args[i])>0 :
                    if args[i][0]==" ":
                        return False,"运行参数首位不能为空格"
                    if args[i][-1]==" ":
                        return  False,"运行参数尾部不能为空格"
                    if "  " in args[i]:
                        return  False,"运行参数中间以单个空格分隔！"
            elif i=="filename":
                if args[i].strip()=="":
                    return  False,"执行命令不能为空！"
        return True

class CronMgr(object):
    "计划任务管理器"
    BUFF={}
    status_config= {-1:"禁用",1:"启用",0:"待部署",2:"正在部署",3:"部署失败"}
    @classmethod
    @defer.inlineCallbacks
    def _init(cls,tid,initcode=True):
        try:
            tid=int(tid)
            result=yield  run_conn_fun("runQuery","select ip,svnpath,svnuser,svnpasswd,version,rule    from   cron_task WHERE  tid=%s",(tid,))
            ip,svnpath,svnuser,svnpasswd,svnversion,rule=result[0]
            if  initcode==True:
                _defer =SubRpc().xmlrpc_init(int(tid),svnpath,int(svnversion),svnuser,svnpasswd)
                set_time_out(2,_defer)
                try:
                    yield  _defer
                except defer.CancelledError :
                    pass
            else:
                pass
            if not  cls.BUFF.has_key(tid):
                pass
            else:
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
            schedule=CronSchedule(rule)
            sc=ScheduledCall(cls._run,tid)
            sc.start(schedule)
            cls.BUFF[tid]=sc
            defer.returnValue(True)
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def _valid_exist(cls,tid,status=None):
        "验证一个tid的task是否存在"
        try:
            tid= int(tid)
            info=yield  run_conn_fun("runQuery","select ip,svnpath,version,svnuser,svnpasswd,rule,status  from   cron_task WHERE  tid=%s",(tid,))
            if len(info)==0:
                defer.returnValue((False,"该cron不存在！"))
            if status==None:
                defer.returnValue(True)
            else:
                assert  type(status) in (int,list,tuple,long)
                if info[0][6] in (([status ]) if type(status) in (int,long) else status) :
                    defer.returnValue(True)
                else:
                    defer.returnValue((False,"该cron状态为{0}".format(cls.status_config[info[0][6]])))
        except Exception as e:
            defer.returnValue((False,str(e)))

    @classmethod
    @defer.inlineCallbacks
    def add(cls,name,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,args,filename):
        "增加"
        try:
            valid_result= Valid().valid_cronadd(name,rule,svnpath,svnversion,svnuser,svnpasswd,info,args,filename)
            ip=localip
            if valid_result!=True:
                defer.returnValue(valid_result)
            def operatedb(cursor,args):
                cursor.execute('''insert into    cron_task(name,  ip, addtime, edittime,
                                rule, status, svnpath, version, svnuser, svnpasswd, info, owner,args,filename)
                                  VALUES(%s,%s,UNIX_TIMESTAMP(),UNIX_TIMESTAMP(),
                                  %s,0,%s,%s,%s,%s,%s,%s,%s,%s)''',args)
                return cursor.lastrowid
            tid= yield  run_conn_fun("runInteraction",operatedb,(name,ip,rule,svnpath,svnversion,svnuser,svnpasswd,info,owner,args,filename))
            tid=int(tid)
            result= yield  cls._init(tid)
            defer.returnValue(result)
        except Exception as e:
            defer.returnValue((False,str(e)))

    @classmethod
    @defer.inlineCallbacks
    def modify(cls,tid,name,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,args,filename):
        "修改cron"
        try:
            print "modify~!!!"
            tid=int(tid)
            valid_result= Valid().valid_cronadd(name,rule,svnpath,svnversion,svnuser,svnpasswd,info,args,filename)
            ip=localip
            if valid_result!=True:
                defer.returnValue(valid_result)
            svnversion=int(svnversion)
            exist_result=yield cls._valid_exist(tid,status=[-1,1,3])
            if exist_result!=True:
                defer.returnValue(exist_result)
            result=yield  run_conn_fun("runQuery","select ip,svnpath,version,svnuser,svnpasswd,rule,status   from   cron_task WHERE  tid=%s",(tid,))
            print "start updatedb"
            yield  run_conn_fun("runOperation","update   cron_task  SET  name=%s,ip=%s,svnpath=%s,version=%s,svnuser=%s,svnpasswd=%s,rule=%s,info=%s,owner=%s,args=%s ,filename=%s  WHERE tid=%s",
                        (name,ip,svnpath,int(svnversion),svnuser,svnpasswd,rule,info,owner,args,filename ,int(tid)))
            status=result[0][6]
            if status ==3:
                _result=True
                if result[0:5]!=(ip,svnpath,svnversion,svnuser,svnpasswd):
                    _result=yield  cls._init(tid,initcode=True)
            else:
                if result[0][0:3]==(ip,svnpath,svnversion):
                    _result= yield  cls._init(tid,initcode=False)
                else:
                    _result= yield cls._init(tid)
            defer.returnValue(_result)
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def stop(cls,tid):
        "禁用"
        try:
            tid=int(tid)
            exist_result=yield cls._valid_exist(tid,status=1)
            if exist_result!=True:
                defer.returnValue(exist_result)
            yield  SubRpc().xmlrpc_stop(tid)
            if cls.BUFF.has_key(tid) :
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
            yield  run_conn_fun("runOperation","update   cron_task set status=-1 WHERE  tid=%s",(tid,))
            defer.returnValue(True)
        except Exception as e :
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def start(cls,tid):
        "启用"
        try:
            tid=int(tid)
            exist_result=yield cls._valid_exist(tid,status=-1)
            if exist_result!=True:
                defer.returnValue(exist_result)
            _result= yield cls._init(tid,initcode=False)
            if _result==True:
                yield  run_conn_fun("runOperation","update   cron_task set status=1 WHERE  tid=%s",(tid,))
            defer.returnValue(_result)
        except Exception as e :
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def remove(cls,tid):
        "删除"
        try:
            tid=int(tid)
            exist_result=yield  cls._valid_exist(tid)
            if exist_result!=True:
                defer.returnValue(exist_result)
            yield run_conn_fun("runOperation","delete from   cron_task WHERE tid=%s",(tid,))
            if cls.BUFF.has_key(tid):
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
                    del cls.BUFF[tid]
            yield  run_conn_fun("runOperation","delete from   cron_runlog WHERE tid=%s",(tid,))
            defer.returnValue(True)
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def manualrun(cls,tid):
        "立刻触发"
        result=yield cls._run(tid,manual=True)
        defer.returnValue(result)
    @classmethod
    @defer.inlineCallbacks
    def _run(cls,tid,manual=False):
        "run "
        try:
            tid=int(tid)
            exist_result=yield  cls._valid_exist(tid,status=1)
            if exist_result!=True:
                defer.returnValue(exist_result)
            result=yield  run_conn_fun("runQuery","select ip,svnpath,version,args from   cron_task WHERE  tid=%s",(tid,))

            svnpath,version,args=result[0][1:]
            def _add(cursor,args):
                cursor.execute('''insert into   cron_runlog(tid, svnpath, version, crontime, begintime, endtime, status, stderror, stdout,`type`)
                                  VALUES(%s,%s,%s,UNIX_TIMESTAMP(),0,0,0,'','',%s)
                               ''',args)
                return cursor.lastrowid
            print "start runInteraction"
            rid=yield  run_conn_fun("runInteraction",_add,(tid,svnpath,int(version),0 if manual==False  else 1))

            result= yield  SubRpc().xmlrpc_run(tid,rid,args)
            defer.returnValue(result)
        except Exception as e :
            defer.returnValue((False,str(e)))

class DaeMgr(object):
    "后台任务管理器"
    BUFF={}
    status_config= {-1:"禁用",1:"启用",0:"待部署",2:"正在部署",3:"部署失败"}
    @classmethod
    @defer.inlineCallbacks
    def _valid_exist(cls,tid,status=None):
        try:
            tid= int(tid)
            info=yield  run_conn_fun("runQuery","select ip,svnpath,version,svnuser,svnpasswd,status  from   task_task WHERE  tid=%s",(tid,))
            print info
            if len(info)==0:
                defer.returnValue((False,"该后台任务不存在！"))
            if status==None:
                defer.returnValue(True)
            else:
                assert  type(status) in (int,list,tuple,long)
                if info[0][5] in (([status ]) if type(status) in (int,long) else status) :
                    defer.returnValue(True)
                else:
                    defer.returnValue((False,"该后台任务状态为{0}".format(cls.status_config[info[0][5]])))
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def _init(cls,tid,initcode=True):
        try:
            tid=int(tid)
            result=yield  run_conn_fun("runQuery","select ip,svnpath,svnuser,svnpasswd,version      from   task_task WHERE  tid=%s",(tid,))
            ip,svnpath,svnuser,svnpasswd,svnversion =result[0]
            if  initcode==True:
                _defer =SubRpc().xmlrpc_init(tid,svnpath,svnversion,svnuser,svnpasswd,mode="task")
                set_time_out(2,_defer)
                try:
                    yield  _defer
                except defer.CancelledError :
                    pass
            else:
                pass
            if not  cls.BUFF.has_key(tid):
                pass
            else:
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
                else:
                    pass
                del cls.BUFF[tid]
            _task=task.LoopingCall(cls._check,tid)
            _task.start(60,now=False)  #检测间隔秒数
            yield  cls._check(tid)
            cls.BUFF[tid]=_task
            defer.returnValue(True)
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def _check(cls,tid):
        print "begin check!",tid
        try:
            tid=int(tid)
            valid_exist=yield  cls._valid_exist(tid,status=1)
            if valid_exist!=True:
                defer.returnValue(valid_exist)
            result=yield  run_conn_fun("runQuery","select ip,tid,args,svnpath,version  from   task_task WHERE  tid=%s",(int(tid),))
            ip,tid,args,svnpath,svnversion=map(lambda i:int(i) if type(i) not  in (str,unicode) else i  ,result[0])
            tidstatus=yield  SubRpc().xmlrpc_getstatus(tid,mode="task")
            print tid,tidstatus
            if tidstatus==False:
                def operate_db(cursor,args):
                    cursor.execute('''insert into   task_runlog(tid, svnpath, version, crontime, begintime, endtime, status, stderror, stdout, `type`)
                                      VALUES(%s,%s,%s,UNIX_TIMESTAMP(),0,0,0,'','',0)''',args)
                    a= cursor.lastrowid
                    return a
                rid=yield  run_conn_fun("runInteraction",operate_db,(tid,svnpath,int(svnversion)))
                yield   SubRpc().xmlrpc_run(tid,rid,args,"task")
                defer.returnValue(True)
            else:
                pass
        except Exception as e:
            print e
            defer.returnValue((False,str(e)))

    @classmethod
    @defer.inlineCallbacks
    def add(cls,name,svnpath,svnversion,svnuser,svnpasswd,info,owner,args,filename):
        "增加"
        try:
            valid_result= Valid().valid_deaadd(name,svnpath,svnversion,svnuser,svnpasswd,info,args,filename)
            ip=localip
            if valid_result!=True:
                defer.returnValue(valid_result)
            def operate_db(cursor,args):
                cursor.execute('''insert into   task_task(name,  ip, addtime, edittime, status,
                                 svnpath, version, svnuser, svnpasswd, info, owner,args,filename )
                                  VALUES(%s,%s,UNIX_TIMESTAMP(),UNIX_TIMESTAMP(),0,
                                  %s,%s,%s,%s,%s,%s,%s,%s)''',args)
                return  cursor.lastrowid
            tid= yield  run_conn_fun("runInteraction",operate_db,(name,ip,svnpath,int(svnversion),svnuser,svnpasswd,info,owner,args,filename))
            tid=int(tid)
            result= yield  cls._init(tid)
            defer.returnValue(result)
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def modify(cls,tid,name,svnpath,svnversion,svnuser,svnpasswd,info,args,filename):
        "修改"
        try:
            tid=int(tid)
            valid_result= Valid().valid_deaadd(name,svnpath,svnversion,svnuser,svnpasswd,info,args,filename)
            ip=localip
            if valid_result!=True :
                defer.returnValue(valid_result)
            exist_result= yield  cls._valid_exist(tid,status=[1,-1,3])
            if exist_result!=True:
                defer.returnValue(exist_result)
            svnversion=int(svnversion)
            result=yield  run_conn_fun("runQuery","select ip,svnpath,version,svnuser,svnpasswd,filename,args,status  from   task_task WHERE  tid=%s",(tid,))
            yield  run_conn_fun("runOperation","update   task_task set name=%s,ip=%s,svnpath=%s,version=%s,svnuser=%s, svnpasswd=%s,info=%s,args=%s , filename=%s  WHERE  tid=%s",
                                      (name,ip,svnpath,svnversion,svnuser,svnpasswd,info,args,filename ,tid))
            _ip,_svnpath,_version,_svnuser,_svnpasswd,_filename,_args,status=result[0]

            if status==1:
                _result=True
                if (svnpath,svnversion)!=(_svnpath,_version) or (filename,args)!=(_filename,_args) :
                    yield  SubRpc().xmlrpc_stop(tid,mode="task")
                    if (svnpath,svnversion)!=(_svnpath,_version):
                        _result=yield cls._init(tid,initcode=True)
                    else:
                        _result=yield cls._init(tid,initcode=False)
            elif status==-1:
                _result=True
                if (svnpath,svnversion)!=(_svnpath,_version):
                    _result=yield  cls._init(tid,initcode=True)
            elif status==3:
                _result=True
                if (svnpath,svnversion,svnuser,svnpasswd)!=(_svnpath,_version,_svnuser,_svnpasswd):
                    _result=yield  cls._init(tid,initcode=True)
            defer.returnValue(_result)
        except Exception as e:
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def stop(cls,tid):
        "禁用"
        try:
            tid=int(tid)
            exist_result=yield cls._valid_exist(tid,status=1)
            if exist_result!=True:
                defer.returnValue(exist_result)
            yield SubRpc().xmlrpc_stop(tid,mode="task")
            if cls.BUFF.has_key(tid):
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
            yield run_conn_fun("runOperation","update   task_task  set  status=-1 WHERE  tid=%s",(tid,))
            defer.returnValue(True)
        except Exception as e :
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def start(cls,tid):
        "启用"
        try:
            tid=int(tid)
            exist_result=yield cls._valid_exist(tid,status=-1)
            if exist_result!=True:
                defer.returnValue(exist_result)
            yield  run_conn_fun("runOperation","update   task_task set status=1 WHERE  tid=%s",(tid,))
            result=yield  cls._init(tid,initcode=False)
            #yield cls._check(tid)
            if result==True:
                defer.returnValue(True)
            else:
                yield  run_conn_fun("runOperation","update   task_task set status=-1 WHERE  tid=%s",(tid,))
                defer.returnValue(result)
        except Exception as e :
            defer.returnValue((False,str(e)))
    @classmethod
    @defer.inlineCallbacks
    def remove(cls,tid):
        "删除"
        try:
            tid=int(tid)
            exist_result=yield cls._valid_exist(tid)
            if exist_result!=True:
                defer.returnValue(exist_result)
            yield  SubRpc().xmlrpc_stop(tid,mode="task")
            if cls.BUFF.has_key(tid):
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
                del cls.BUFF[tid]
            yield  run_conn_fun("runOperation","delete from    task_task where tid=%s",(tid,))
            yield  run_conn_fun("runOperation","delete from   task_runlog WHERE tid=%s",(tid,))
            defer.returnValue(True)
        except Exception as e :
            defer.returnValue((False,str(e)))

    @classmethod
    @defer.inlineCallbacks
    def restart(cls,tid):
        "重启"
        try:
            tid=int(tid)
            exist_result=yield cls._valid_exist(tid,status=1)
            if exist_result!=True:
                print exist_result
                defer.returnValue(exist_result)
            if cls.BUFF.has_key(tid):
                if cls.BUFF[tid].running:
                    cls.BUFF[tid].stop()
                del cls.BUFF[tid]
            yield  SubRpc().xmlrpc_stop(tid,mode="task")
            result=yield  cls._init(tid,initcode=False)
            if result==True:
                yield run_conn_fun("runOperation","update   task_task  set  status=1 WHERE  tid=%s",(tid,))
            defer.returnValue(result)
        except Exception as e :
            defer.returnValue((False,str(e)))


class MainRpc(xmlrpc.XMLRPC):
    def __init__(self):
        xmlrpc.XMLRPC.__init__(self,allowNone=True)
        self.cronmgr=CronMgr()
        self.deamgr=DaeMgr()

    @defer.inlineCallbacks
    def _run(self,funname,mode,*args):
        try:
            function=getattr(self.cronmgr if mode=="cron" else self.deamgr ,funname)
            result=yield function(*args)
            print result
            defer.returnValue(result)
        except Exception as e :
            print e
            defer.returnValue((False,str(e)))

    # ——---------------------------------cron--------------------------------
    @defer.inlineCallbacks
    def xmlrpc_addcron(self,name,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,args,filename):
        "增加一个Cron, 返回值 True,123  或者False,‘失败’ "
        result=yield self._run("add","cron",name,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,args,filename)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_removecron(self,tid):
        "删除一个cron"
        result=yield self._run("remove","cron",tid)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_modifycron(self,tid,name,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,args,filename):
        "更改一个cron"
        print "modifycron!"
        result=yield self._run("modify","cron",tid,name,svnpath,svnversion,svnuser,svnpasswd,rule,info,
                               owner,args,filename)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_stopcron(self,tid):
        "禁用一个cron"
        result=yield  self._run("stop","cron",tid)
        defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_startcron(self,tid):
        "启用一个cron"
        result=yield self._run("start","cron",tid)
        defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_runcron(self,tid):
        "立刻触发这个cron"
        result=yield  self._run("manualrun","cron",tid)
        defer.returnValue(result)
    # -----------------------------------后台任务------------------------------
    @defer.inlineCallbacks
    def xmlrpc_adddaemon(self,name,svnpath,svnversion,svnuser,svnpasswd,info,owner,args,filename):
        "增加一个后台任务  "
        result=yield  self._run("add","dae", name,svnpath,svnversion,svnuser,svnpasswd ,info,owner,args,filename )
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_removedaemon(self,tid):
        "删除一个后台任务"
        result=yield  self._run("remove","dae",tid)
        defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_modifydaemon(self,tid,name,svnpath,svnversion,svnuser,svnpasswd,info,args,filename):
        "修改一个后台任务"
        "print modify"
        result= yield  self._run("modify","dae", tid,name,svnpath,svnversion,svnuser,svnpasswd,info,args,filename)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_stopdaemon(self,tid):
        "禁用一个后台任务"
        result=yield self._run("stop","dae",tid)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_startdaemon(self,tid):
        "启用一个后台任务"
        result=yield  self._run("start","dae",tid)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_restartdaemon(self,tid):
        "重启一个后台任务"
        result=yield  self._run("restart","dae",tid)
        defer.returnValue(result)

    def xmlrpc_getstatusdaemon(self,tid):
        "获取一个应用当前的运行状态"
        return SubRpc().xmlrpc_getstatus(tid,"task")

    def xmlrpc_mgetstatusdaemon(self,tidlist):
        "获取多个应用当前的运行状态"
        return dict( [ (str(tid),SubRpc().xmlrpc_getstatus(tid,"task")) for tid in  tidlist])

import socket
import  os
localip=None
from crondeamon.common.valid_configfile import valid_config
@defer.inlineCallbacks
def init():
    config=valid_config()
    mysqlhost=config["mysqlhost"]
    mysqlport=int(config["mysqlport"])
    mysqldb=config["mysqldb"]
    mysqluser=config["user"]
    mysqlpasswd=config["passwd"]
    datadir=config["datadir"]
    globals()["datadir"]=datadir
    host=config["host"]
    mysqlcharset=config["charset"]
    MYSQLCONFIG["host"]=mysqlhost
    MYSQLCONFIG["port"]=mysqlport
    MYSQLCONFIG["db"]=mysqldb
    MYSQLCONFIG["user"]=mysqluser
    MYSQLCONFIG["passwd"]=mysqlpasswd
    MYSQLCONFIG["charset"]=mysqlcharset
    global  localip
    localip=host
    global conn
    from ..common.valid_mysql import valid,add_server
    valid(MYSQLCONFIG["host"],MYSQLCONFIG["port"],MYSQLCONFIG["db"],MYSQLCONFIG["user"],MYSQLCONFIG["passwd"])
    add_server(MYSQLCONFIG["host"],MYSQLCONFIG["port"],MYSQLCONFIG["db"],MYSQLCONFIG["user"],MYSQLCONFIG["passwd"],
               host)
    conn=adbapi.ConnectionPool("MySQLdb",host=MYSQLCONFIG["host"],user=MYSQLCONFIG["user"],
                               passwd=MYSQLCONFIG["passwd"],charset=MYSQLCONFIG["charset"],
                               port=MYSQLCONFIG["port"],db=MYSQLCONFIG["db"],cp_reconnect=True)
    result_cron=yield  run_conn_fun("runQuery","select tid from   cron_task WHERE ip=%s and status=1",(localip,))
    result_dae=yield   run_conn_fun("runQuery","select tid from   task_task WHERE ip=%s and status=1",(localip,))
    if len(result_cron)==0:
        pass
    else:
        if len(result_cron)==1:
            result_cron=result_cron*2
        yield  run_conn_fun("runOperation","update cron_runlog set status=3 WHERE  status in (0,1) and tid in %s",
                            (tuple([i[0] for i in result_cron]),))
    if len(result_dae)==0:
        pass
    else:
        if len(result_dae)==1:
            result_dae*=2
        yield  run_conn_fun("runOperation","update task_runlog set status=3  WHERE   status in (0,1) and tid in %s",
                            (tuple([i[0] for i in result_dae]),))
    cronmgr=CronMgr()
    deamgr=DaeMgr()
    for i in result_cron:
        yield  cronmgr._init(i[0],initcode=False)
    for j in result_dae:
        yield  deamgr._init(j[0],initcode=False)
        print "init one dae"
    defer.returnValue("init Success!")
def _print(a):
        print a
def print_cron():
    CRON_DICT=CronMgr.BUFF
    for i in CRON_DICT:
        if CRON_DICT[i].running:
            pass
init().addCallback(_print).addErrback(_print)