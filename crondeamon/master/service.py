# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/24.
# ---------------------------------
from twisted.web import  http_headers,html,http
from twisted.web import  xmlrpc,server,resource
from twisted.internet import  reactor,task,defer
from twisted.enterprise import  adbapi
import  ConfigParser

SUBPORT=8014
MYSQLCONFIG={}
def mysql_config_init():
    global  MYSQLCONFIG
    cfg=ConfigParser.ConfigParser()
    result=cfg.read("/etc/crondeamon/master.ini")
    try:
        assert  result== ["/etc/crondeamon/master.ini"]
        assert cfg.sections()==["crondeamon"]
        config=dict(cfg.items("crondeamon"))
        host=config["host"]
        mysqlhost=config["mysqlhost"]
        mysqlport=int(config["mysqlport"])
        mysqldb=config["mysqldb"]
        mysqluser=config["user"]
        mysqlpasswd=config["passwd"]
        mysqlcharset=config["charset"]
    except:
        raise Exception("Config File /etc/crondeamon/master.ini is error please recheck it!")
    else:
        MYSQLCONFIG["host"]=mysqlhost;MYSQLCONFIG["port"]=mysqlport;MYSQLCONFIG["user"]=mysqluser
        MYSQLCONFIG["passwd"]=mysqlpasswd
        MYSQLCONFIG["charset"]=mysqlcharset;MYSQLCONFIG["db"]=mysqldb

mysql_config_init()
@defer.inlineCallbacks
def run_conn_fun(fun,*args):
    "运行"
    conn=adbapi.ConnectionPool("MySQLdb",host=MYSQLCONFIG["host"],user=MYSQLCONFIG["user"],passwd=MYSQLCONFIG["passwd"],charset=MYSQLCONFIG["charset"],port=MYSQLCONFIG["port"],db=MYSQLCONFIG["db"])
    result=yield  getattr(conn,fun)(*args)
    conn.close()
    defer.returnValue(result)
class MainRpc(xmlrpc.XMLRPC):

    @defer.inlineCallbacks
    def _run(self,funname,ip,*args):
        try:
            serve=xmlrpc.Proxy("http://%s:%s"%(ip,SUBPORT),allowNone=True,connectTimeout=2.0)
            result=yield  serve.callRemote(funname,*args)
            defer.returnValue(result)
        except Exception as e :
            defer.returnValue((False,str(e)))
    @defer.inlineCallbacks
    def _get_ip(self,tid,mode):
        try:
            if mode=="cron":
                info= yield run_conn_fun("runQuery","select ip from  cron_task WHERE  tid=%s",(tid,))
            else:
                info= yield  run_conn_fun("runQuery","select ip from  task_task WHERE  tid=%s",(tid,))
            if len(info)==0:
                defer.returnValue((False,"该{0}不存在！".format("计划任务" if mode=="cron" else "后台任务")))
            else:
                defer.returnValue(info[0][0])
        except Exception as e :
            defer.returnValue((False,str(e)))
    @defer.inlineCallbacks
    def _mget_ip(self,tidlist,mode):
        tidlist=[str(i) for i in tidlist]
        result=dict(zip(tidlist,len(tidlist)*[None]))
        if len(tidlist)==1:
            tidlist*=2
        tidlist=[int(i) for i in tidlist]
        try:
            if mode=="cron":
                info=yield  run_conn_fun("runQuery","select ip,tid from cron_task WHERE  tid in %s",(tuple(tidlist),))
            else:
                info=yield  run_conn_fun("runQuery","select ip,tid from task_task WHERE  tid in %s",(tuple(tidlist),))
            for i,j in info:
                result[str(j)]=i
            defer.returnValue((True,result))
        except Exception as e :
            defer.returnValue((False,str(e)))

    # ——---------------------------------cron--------------------------------
    @defer.inlineCallbacks
    def xmlrpc_addcron(self,ip,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom='',branch=''):
        "增加一个Cron, 返回值 True,123  或者False,‘失败’ "
        if branch!='':
            result=yield self._run("addcron",ip,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom,branch)
        else:
            result=yield self._run("addcron",ip,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom)
        defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_multiaddcron(self,iplist,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom='',branch=''):
        "批量增加Cron， 返回值True,[1,2,3] 或者False,'失败' "
        if branch!='':
            defer_list=[self._run("addcron",ip,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom,branch )    for ip in  iplist]
        else:
            defer_list=[self._run("addcron",ip,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom)    for ip in  iplist]

        results=yield  defer.DeferredList(defer_list,consumeErrors=True)
        buff=  map(lambda i:True if i==(True,True) else False  ,results   )
        defer.returnValue(buff)

    @defer.inlineCallbacks
    def xmlrpc_removecron(self,tid):
        "删除一个cron"
        info=yield  self._get_ip(tid,mode="cron")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield self._run("removecron",ip,tid)
            defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_modifycron(self,ip, tid,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom="",branch=''):
        "更改一个cron"
        print locals()
        if branch!='':
            result=yield self._run("modifycron",ip,tid,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom,branch )
        else:
            result=yield self._run("modifycron",ip,tid,name,project,app,svnpath,svnversion,svnuser,svnpasswd,rule,info,owner,_type,args,filename,custom)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_stopcron(self,tid):
        "禁用一个cron"
        info=yield  self._get_ip(tid,mode="cron")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield  self._run("stopcron",ip,tid)
            defer.returnValue(result)

    @defer.inlineCallbacks
    def xmlrpc_startcron(self,tid):
        "启用一个cron"
        info=yield  self._get_ip(tid,mode="cron")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield self._run("startcron",ip ,tid)
            defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_runcron(self,tid):
        "立刻触发这个cron"
        info=yield  self._get_ip(tid,mode="cron")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield  self._run("runcron",ip ,tid)
            defer.returnValue(result)
    # -----------------------------------后台任务------------------------------
    @defer.inlineCallbacks
    def xmlrpc_adddaemon(self,ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd,info,owner,_type,args,filename,custom='',num=1,branch=''):
        "增加一个后台任务  "
        print "num:",num
        if branch!="":
            if custom!='':
                defer_list=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,custom,branch) for i in ([""]*num)]
            else:
                defer_list=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,'',branch) for i in ([""]*num)]
        else:
            if custom!='':
                defer_list=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,custom) for i in ([""]*num)]
            else:
                defer_list=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,'') for i in ([""]*num)]
        results=yield  defer.DeferredList(defer_list,consumeErrors=True)
        buff=map(lambda i:True if i ==(True,True) else False,results)
        defer.returnValue(buff)
    @defer.inlineCallbacks
    def xmlrpc_multiadddaemon(self,iplist,name,project,app,svnpath,svnversion,svnuser,svnpasswd,info,owner,_type,args,filename,custom='',num=1,branch=''):
        "批量增加后台任务"
        defer_list=[]
        if branch!='':
            if custom!='':
                for i in [""]*num:
                    defer_list+=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,custom,branch)   for ip in iplist ]
            else:
                for i in [""]*num:
                    defer_list+=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,'',branch)   for ip in iplist ]
        else:
            if custom!='':
                for i in [""]*num:
                    defer_list+=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,custom)   for ip in iplist ]
            else:
                for i in [""]*num:
                    defer_list+=[self._run("adddaemon",ip, name,project,app,svnpath,svnversion,svnuser,svnpasswd ,info,owner,_type,args,filename,'')   for ip in iplist ]
        print defer_list
        results=yield  defer.DeferredList(defer_list,consumeErrors=True)
        print results
        buff=  map(lambda i:True if i==(True,True) else False  ,results)
        defer.returnValue(buff)

    @defer.inlineCallbacks
    def xmlrpc_removedaemon(self,tid):
        "删除一个后台任务"
        info=yield  self._get_ip(tid,mode="dae")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield  self._run("removedaemon",ip,tid)
            defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_modifydaemon(self,ip, tid,name,project,app,svnpath,svnversion,svnuser,svnpasswd,info,_type,args,filename,custom='',branch=''):
        "修改一个后台任务"
        if branch!="":
            result= yield  self._run("modifydaemon",ip , tid,name,project,app,svnpath,svnversion,svnuser,svnpasswd,info,_type,args,filename,custom,branch)
        else:
            result= yield  self._run("modifydaemon",ip , tid,name,project,app,svnpath,svnversion,svnuser,svnpasswd,info,_type,args,filename,custom)
        defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_stopdaemon(self,tid):
        "禁用一个后台任务"
        info=yield  self._get_ip(tid,mode="dae")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield self._run("stopdaemon",ip ,tid)
            defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_startdaemon(self,tid):
        "启用一个后台任务"
        info=yield  self._get_ip(tid,mode="dae")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield  self._run("startdaemon",ip  ,tid)
            defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_restartdaemon(self,tid):
        "重启一个后台任务"
        info=yield  self._get_ip(tid,mode="dae")
        if type(info)==tuple:
            defer.returnValue(info)
        else:
            ip=info
            result=yield  self._run("restartdaemon",ip ,tid)
            defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_getstatusdaemon(self,tid,ip=None):
        if ip ==None:
            info=yield  self._get_ip(tid,mode="dae")
            if type(info)==tuple:
                defer.returnValue(info)
            else:
                ip=info
        else:
            pass
        result=yield  self._run("getstatusdaemon",ip,tid)
        defer.returnValue(result)
    @defer.inlineCallbacks
    def xmlrpc_mgetstatusdaemon(self,tidlist):
        result=yield  self._mget_ip(tidlist,"dae")

        if result[0]==False:
            defer.returnValue(result)
        else:
            tiddict=result[1]
            _tidlist=[i for i  in  tiddict.keys() if tiddict[i]!=None]
            defer_list=[self._run("getstatusdaemon",tiddict[str(tid)],int(tid))   for tid  in _tidlist]
            deferlist=defer.DeferredList(defer_list,consumeErrors=True)
            deferlist_result=yield  deferlist

            buff={}
            for tid,(defer_status,defer_result) in zip(_tidlist,deferlist_result):
                if defer_status==False:
                    buff[str(tid)]=None
                elif defer_status==True:
                    buff[str(tid)]=defer_result
            for i in tidlist:
                if not buff.has_key(str(i)):
                    buff[str(i)]=None

            defer.returnValue(buff)
