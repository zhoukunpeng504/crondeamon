#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/8.
# ---------------------------------
import  xmlrpclib
from cap.settings import CRON_SERVER
import  socket
from cap.utils import get_svn_top_version
def get_cron_serve():
    serve=xmlrpclib.ServerProxy("http://%s:%s"%(CRON_SERVER["host"],CRON_SERVER["port"]),allow_none=True)
    return serve
def valid_ip(ip):
    print 'IP:',ip
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
def valid_input(ip,name,rule,svnpath,version,svnuser,svnpasswd,info,args,filename):
    args=locals()
    _config={"rule":"时间规则","svnpath":"SVN url","svnuser":"svn user","svnpasswd":"svn passwd","info":"功能描述",
             "project":"所属应用-项目","app":"所属应用-应用","name":"名称","args":"运行参数","filename":"执行文件名"}
    for i in args:
        if i in ("rule","svnpath","svnuser","svnpasswd","info","project","app","name"):
            if args[i]=='':
                return False,"{0}不能为空".format(_config[i])
            if i=="name" and " " in args[i]:
                return False,"名称中不能包含空格！"
        elif i in ("version",):
            try :
                if args[i] =="*":
                    pass
                else:
                    int(args[i])
            except:
                return False,"版本不合法！"
        elif i =="_type":
            if args[i] not in ("1","2","3"):
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
            if len(args[i])==0 or args[i].strip()=="":
                return  False,"执行命令不能为空"
    return True