#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/15.
# ---------------------------------
from django.db.models.query import  Q,QuerySet
from django.db.models import  Count,Max
from models import Task ,Runlog
import  socket
from cap.settings import  TASK_SERVE
import  xmlrpclib
from models import Task
from django.db import  connection


def valid_tid(request):
    "验证一个tid的task是否存在，返回True,task  或者False"
    getinfo=request.GET
    try:
        tid=getinfo.get("tid")
        tid=int(tid)
        task=Task.objects.get(pk=tid)
        return True,task
    except:
        return False

def generate_dict(status,message):
    return locals()

def  run_serve_fun(funname,*args):
    serve=get_task_serve()
    try:
        fun=getattr(serve,funname)
        result=fun(*args)
        return result
    except Exception as e:
        return False,str(e)




def get_task_serve():
    serve=xmlrpclib.ServerProxy("http://%s:%s"%(TASK_SERVE["host"],TASK_SERVE["port"]),allow_none=True)
    return serve

def add_fail_count_to_tasklist(tasklist):
    tid_list=[i.tid for i in  tasklist]
    buff={}
    for i in tasklist:
        buff[i.tid]=i
    if len(tid_list)==0:
        pass
        return True
    for i in tasklist:
        i.count=0
    if len(tid_list)==1:
        tid_list*=2
    tid_tuple=tuple(tid_list)
   # _query= Runlog.objects.filter(tid__in=tid_list).query
    #_query.group_by=["tid"]
    #_buff=QuerySet(query=_query,model=Runlog)
    #_result=_buff.annotate(count=Count("rid"))
    cursor=connection.cursor()
    cursor.execute("SELECT `task_runlog`.`rid`, `task_runlog`.`tid`,COUNT(`task_runlog`.`rid`) AS `count` FROM `task_runlog` WHERE `task_runlog`.`tid` IN %s GROUP BY tid;",(tid_tuple,))
    _result=cursor.fetchall()
    for _rid,_tid,_count  in _result:
        buff[_tid].count=int(_count)
    return True
def add_run_status_to_tasklist(tasklist):

    tid_list=[i.tid for i in tasklist]
    buff={}
    for i in tasklist:
        buff[i.tid]=i
    if len(tid_list)==0:
        pass
        return True
    else:
        # try:
        mstatus=get_task_serve().mgetstatusdaemon(tid_list)
        for  i in mstatus:
            if mstatus[i]==True:
                mstatus[i]=1
            elif mstatus[i]==False:
                mstatus[i]=2
            else:
                mstatus[i]=0
        print mstatus
        # except:
        #     mstatus=None
        for i in tasklist:
            if mstatus!=None:
                i.running=mstatus[str(i.tid)]
            else:
                i.running=0
    return True


def valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False
def valid_ip_list(ip_list):
    "验证IP列表"
    result=[valid_ip(i)  for i in ip_list]
    if False in result:
        return False
    else:
        return True
def valid_input(ip,name,svnpath,version,svnuser,svnpasswd,info,args,filename):
    args=locals()
    _config={"rule":"时间规则","svnpath":"SVN url","svnuser":"svn user","svnpasswd":"svn passwd","info":"功能描述",
             "project":"所属应用-项目","app":"所属应用-应用","name":"名称"}
    for i in args:
        if i in ("svnpath","svnuser","svnpasswd","info","project","app","name"):
            if args[i]=='':
                return False,"{0}不能为空".format(_config[i])
            if i=="name" and " " in args[i] :
                return False,"名称中不能包含空格！"
        elif i in ("version",):
            try :
                if args[i]=="*":
                    pass
                else:
                    int(args[i])
            except:
                return False,"版本不合法！"
        elif i =="_type":
            if args[i] not in ("1","2"):
                return False,"非法类型参数！"
        elif i =="ip":
            if ip==None:
                return False,"至少选择一个IP！"
            result=valid_ip(ip) if type(ip) in (str,unicode) else  valid_ip_list(ip)
            if result==False:
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
            if len(args[i])=="" or args[i].strip()=="" :
                return  False,"执行命令不能为空！"
    return True




