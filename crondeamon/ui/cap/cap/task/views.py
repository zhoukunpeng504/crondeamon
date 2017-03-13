#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/15.
# ---------------------------------
import  json
from django.http import  HttpResponse, HttpResponseRedirect,HttpResponseServerError
from django.http import  HttpRequest
from django.template.response import RequestContext
from django.shortcuts import  render_to_response
from django.core.paginator import  Paginator,InvalidPage
from django.contrib.auth.decorators import login_required
from models import Task,Runlog
from cap.cron.models import  CronServe
from django.db.models.query import  Q,QuerySet
from  utils import  add_fail_count_to_tasklist,valid_input,get_task_serve,add_run_status_to_tasklist
from utils import valid_tid,run_serve_fun
from django.contrib.admin.models import  User
from  cap.utils import  valid_group_required,get_svn_top_version

import  sys
reload(sys)
sys.setdefaultencoding("utf-8")

@login_required
def home(request):
    "home"
    return  HttpResponseRedirect("/task/manage/")

@login_required
def add(request):
    "增加一个task"
    getinfo=request.GET
    postinfo=request.POST
    if getinfo.has_key("data"):
        datatype=getinfo.get("data")
        if datatype=="table":
            u"表格数据填充"
            pageindex=getinfo.get("page")
            pageindex=int(pageindex)
            rowsnum=getinfo.get("rows")
            rowsnum=int(rowsnum)
            _task=Task.objects.all().order_by("-tid")
            buff={}
            task_pageobj=Paginator(_task,rowsnum)
            buff["records"]=_task.count()
            buff["total"]=task_pageobj.num_pages
            try:
                task_list=task_pageobj.page(pageindex)
            except:
                task_list=task_pageobj.page(task_pageobj.num_pages)
            add_fail_count_to_tasklist(task_list)
            add_run_status_to_tasklist(task_list)
            buff["page"]=task_list.number
            buff["rows"]=[{"cell":[i.tid,i.name,i.get_status(),[i.running,i.count],i.project,i.app,i.get_info() ,i.owner ,i.ip]}  for i in task_list]
        elif datatype=="add":
            u"增加一个Task"
            ip=postinfo.get("ip")
            name=postinfo.get("name")
            svnpath=postinfo.get("url").strip()
            version=postinfo.get("version")
            svnuser=postinfo.get("svnuser")
            svnpasswd=postinfo.get("svnpasswd")
            info=postinfo.get("fn")
            args=""
            filename=postinfo.get("filename")
            buff={}
            valid_result= valid_input(ip,name,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if valid_result!=True:
                buff["status"],buff["message"]=valid_result
            else:
                if version=="*":
                    versioninfo=get_svn_top_version(svnurl=svnpath,svnuser=svnuser,svnpasswd=svnpasswd)
                    if versioninfo[0]==False:
                        buff["status"],buff["message"]=versioninfo
                    else:
                        version=versioninfo[1]
                if buff=={}:
                    serve=get_task_serve()
                    try:
                        result=serve.adddaemon(name,svnpath,str(version),svnuser,svnpasswd,info,request.user.username,args,filename)
                        if True == result:
                            buff["status"],buff["message"]= True,u"创建成功！"
                        else:
                            buff["status"],buff["message"]=False,u"创建失败！"
                    except Exception as e:
                        buff["status"],buff["message"]=False,str(e)
        return HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
    cronserve=CronServe.objects.all().values()
    return  render_to_response("add_task.html",locals(),context_instance=RequestContext(request))

@login_required
def manage(request):
    "管理task"
    getinfo=request.GET
    postinfo=request.POST
    if getinfo.has_key("data"):
        datatype=getinfo.get("data")
        if datatype=="table":
            "表格数据填充"
            pageindex=getinfo.get("page")
            pageindex=int(pageindex)
            rowsnum=getinfo.get("rows")
            rowsnum=int(rowsnum)
            _task=  Task.objects.all()
            _task= _task.order_by("-tid")

            buff={}
            task_pageobj=Paginator(_task,rowsnum)
            buff["records"]=_task.count()
            buff["total"]=task_pageobj.num_pages
            try:
                task_list=task_pageobj.page(pageindex)
            except:
                task_list=task_pageobj.page(task_pageobj.num_pages)
            add_fail_count_to_tasklist(task_list)
            add_run_status_to_tasklist(task_list)
            buff["page"]=task_list.number
            buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(),[i.running,i.count],"","",i.get_info() ,i.owner,i.ip]}  for i in task_list]
            return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")

    elif getinfo.has_key("ip"):
        ip=getinfo.get("ip")
        status=getinfo.get("status")
        info=getinfo.get("fn")
        owner=getinfo.get("owner")
        rows=getinfo.get("rows","15")
        page=getinfo.get("page","1")
        def handleparam(ip,status,info,owner):
            result=locals()
            if ip=='':
                del result["ip"]
            if owner=='' or owner==None:
                del result["owner"]
            try:
                int(status)
            except:
                del result["status"]
            if info=='':
                del result["info"]
            if result.has_key("info"):
                del  result["info"]
                result["info__icontains"]=info
            return  result
        args=handleparam(ip,status,info,owner)

        task_queryset=Task.objects.filter(**args)
        task_queryset=Task.objects.filter(**args)
        task_queryset= task_queryset.order_by("-tid")
        task_pagiobj=Paginator(task_queryset,int(rows))
        buff={}
        buff["records"]=task_queryset.count()
        buff["total"]=task_pagiobj.num_pages
        try:
            task_list=task_pagiobj.page(int(page))
        except:
            task_list=task_pagiobj.page(1)
        buff["page"]=task_list.number
        add_fail_count_to_tasklist(task_list)
        add_run_status_to_tasklist(task_list)
        buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(), [i.running, i.count],"","",i.get_info(),i.owner ,i.ip]} for  i in task_list]
        return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")


    cronserve=CronServe.objects.all().order_by("ip")
    userinfo=User.objects.all().values("username")
    return  render_to_response("manage_task.html",locals(),context_instance=RequestContext(request))
@login_required
def stoptask(request):
    "stop  one task"
    from  utils import generate_dict
    info= valid_tid(request)
    if info==False:
        buff= generate_dict(False,"该task不存在")
    else:
        task=info[1]
        result= run_serve_fun("stopdaemon",task.tid)
        if result==True:
            buff=generate_dict(True,"Success!")
        else:
            buff=generate_dict(*result)
    return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def starttask(request):
    "start one task"
    info=valid_tid(request)
    from utils import  generate_dict
    if info==False:
        buff=dict([("status",False),("message","该task不存在！")])
    else:
        task=info[1]
        result=run_serve_fun("startdaemon",task.tid)
        if result==True:
            buff=generate_dict(True,"Success!")
        else:
            buff=generate_dict(*result)
    return HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def restarttask(request):
    "restart  one task"
    from utils import  generate_dict
    info=valid_tid(request)
    if info==False:
        buff=generate_dict(False,"该task不存在")
    else:
        task=info[1]
        result=run_serve_fun("restartdaemon",task.tid)
        if result==True:
            buff=generate_dict(True,"Success!")
        else:
            buff=generate_dict(*result)
    return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def removetask(request):
    "删除一个task"
    from utils import  generate_dict
    info=valid_tid(request)
    if info==False:
        buff=generate_dict(False,"该task不存在")
    else:
        task=info[1]
        result=run_serve_fun("removedaemon",task.tid)
        if result==True:
            buff=generate_dict(True,"Success!")
        else:
            buff=generate_dict(*result)
    return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")

@login_required
def runrecord(request):
    "运行记录"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    page=getinfo.get("page",'1')
    rows=getinfo.get("rows","10")
    page,rows=int(page),int(rows)
    buff={}
    task=Task.objects.get(pk=int(tid))
    runlog=Runlog.objects.filter(tid=int(tid)).order_by("-rid")
    buff["records"]=runlog.count()
    paginator=Paginator(runlog,rows)
    buff["total"]=paginator.num_pages
    try:
        page_obj=paginator.page(page)
    except:
        page_obj=paginator.page(paginator.num_pages)
    buff["page"]=page_obj.number
    buff["rows"]=[{"cell":[i.get_type(),i.get_code_info(task),i.get_crondatetime(),i.get_begindatetime(),i.get_enddatetime(),i.get_status(),i.rid]} for i in page_obj]
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")

@login_required
def logdetail(request):
    "运行记录的log"
    getinfo=request.GET
    postinfo=request.POST
    rid=getinfo.get("rid")
    #info=valid_tid(request)
    #if info==False:
    #    return  HttpResponse("Error!")
    #else:
    runlog=Runlog.objects.get(pk=int(rid))
    stdout=runlog.stdout
    stderr=runlog.stderror
    #return  HttpResponse(json.dumps({"stdout":stdout,"stderr":stderr},ensure_ascii=False,indent=True),mimetype="application/javascript")
    return  render_to_response("task_run_log.html",locals(),context_instance=RequestContext(request))
@login_required
def taskdetail(request):
    "task的json详情"
    info=valid_tid(request)
    if info==False:
        buff={}
    else:
        task=info[1]
        buff={"ip":task.ip,"name":task.name,"url":task.svnpath,"version":task.version,

              "svnuser":task.svnuser,"svnpasswd":task.svnpasswd,"fn":task.info,"filename":task.filename}
    return HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")

@login_required
def modifytask(request):
    "更改一个task"
    from utils import generate_dict
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    _ip=postinfo.get("ip")
    ip_list=postinfo.getlist("ip")
    name=postinfo.get("name")
    svnpath=postinfo.get("url").strip()
    version=postinfo.get("version")
    svnuser=postinfo.get("svnuser")
    svnpasswd=postinfo.get("svnpasswd")
    info=postinfo.get("fn")
    _type=postinfo.get("type")
    args=""
    filename=postinfo.get("filename")

    __info=valid_tid(request)
    if __info==False:
        buff=generate_dict(False,"此task非法！")
    else:
        task=__info[1]
        ip=task.ip
        if _ip!=ip:
            buff=generate_dict(False,"不允许修改IP！")
        elif name!=task.name:
            buff=generate_dict(False,"不允许修改后台任务名！")
        elif len(ip_list)>1:
            buff=generate_dict(False,"不可选择多台主机！")
        else:
            result=valid_input(ip,name,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if result!=True:
                buff=generate_dict(*result)
            else:
                if version=="*":
                    versioninfo=get_svn_top_version(svnpath,svnuser,svnpasswd)
                    if versioninfo[0]==False:
                        buff=generate_dict(versioninfo[0],versioninfo[1])
                    else:
                        version=versioninfo[1]
                if  not  locals().has_key("buff"):
                    result= run_serve_fun("modifydaemon",task.tid,name,svnpath,str(version),svnuser,svnpasswd,info,args,filename)
                    if result==True:
                        buff=generate_dict(True,"Success!")
                    else:
                        buff=generate_dict(*result)
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")



