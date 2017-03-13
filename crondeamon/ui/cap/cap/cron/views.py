#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/1.
# ---------------------------------
from django.http import  HttpResponse, HttpResponseRedirect,HttpResponseServerError
from django.http import  HttpRequest
from django.template.response import RequestContext
from django.shortcuts import  render_to_response
from django.core.paginator import  Paginator,InvalidPage
from django.contrib.auth.decorators import login_required
from models import   Task ,RunLog,CronServe
import  socket
from  utils import  get_cron_serve,valid_input,valid_ip
from django.db.models import Q,F
from django.db.models import  ObjectDoesNotExist
from django.contrib.admin.models import User
import  json,random
from cap.utils import valid_group_required,get_svn_top_version

import  sys
reload(sys)
sys.setdefaultencoding("utf-8")
@login_required
def home(request):
    "Home"
    return  HttpResponseRedirect("/cron/manage/")
@login_required
def test(request):
    return  HttpResponse("test")

#----------------------------添加计划任务
@login_required
def add(request):
    "add cron"
    getinfo=request.GET
    postinfo=request.POST
    print getinfo
    print postinfo
    if getinfo.has_key("data"):
        "json data "
        datatype=getinfo.get("data")
        if datatype=="table":
            "表格数据填充"
            pageindex=getinfo.get("page")
            pageindex=int(pageindex)
            rowsnum=getinfo.get("rows")
            rowsnum=int(rowsnum)
            task_queryset= Task.objects.all().order_by("-tid")
            buff={}
            #buff["page"]=pageindex
            task_pagiobj=Paginator(task_queryset,rowsnum)
            buff["records"]=task_pagiobj.count
            buff["total"]=task_pagiobj.num_pages
            try:
                task_list=task_pagiobj.page(pageindex)
            except:
                task_list=task_pagiobj.page(task_pagiobj.num_pages)
            buff["page"]=task_list.number
            buff["rows"]=[{"cell":[i.tid,i.name,i.get_status(),i.rule,i.project,i.app,i.get_info() ,i.get_owner_and_type(),i.ip]}  for i in task_list]
        elif datatype=="add":
            "增加计划任务"
            ip=postinfo.get("ip")
            name=postinfo.get("name")
            rule=postinfo.get("rule")
            svnpath=postinfo.get("url").strip()
            version=postinfo.get("version")
            svnuser=postinfo.get("svnuser")
            svnpasswd=postinfo.get("svnpasswd")
            info=postinfo.get("fn")
            _type=postinfo.get("type")
            args=""
            filename=postinfo.get("filename")
            buff={}

            valie_result=valid_input(ip  ,name,rule,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if  valie_result!=True:
                buff["status"],buff["message"]=valie_result
            else:
                if version=="*":
                    versioninfo=get_svn_top_version(svnurl=svnpath,svnuser=svnuser,svnpasswd=svnpasswd)
                    if versioninfo[0]==False:
                        buff["status"],buff["message"]=versioninfo
                    else:
                        version=versioninfo[1]
                if buff=={}:
                    server=get_cron_serve()

                    result=server.addcron(name,svnpath,str(version),svnuser,svnpasswd,rule,info,
                                              request.user.username,args,filename)
                    if result!=True:
                        buff["status"],buff["message"]=result
                    else:
                        buff["status"]=True
                        buff["message"]="Success!"
            return HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")

    else:
        return  render_to_response("add.html",locals(),context_instance=RequestContext(request))

#--------------------------------计划任务管理
@login_required
def manage(request):
    "cron manage"
    getinfo=request.GET
    postinfo=request.POST
    if getinfo.has_key("data"):
        "json data "
        datatype=getinfo.get("data")
        if datatype=="table":
            "表格数据填充"
            pageindex=getinfo.get("page")
            pageindex=int(pageindex)
            rowsnum=getinfo.get("rows")
            rowsnum=int(rowsnum)
            task_queryset=  Task.objects.all()
            task_queryset= task_queryset.order_by("-tid")
            buff={}
            #buff["page"]=pageindex
            task_pagiobj=Paginator(task_queryset,rowsnum)
            buff["records"]=task_pagiobj.count
            buff["total"]=task_pagiobj.num_pages
            try:
                task_list=task_pagiobj.page(pageindex)
            except:
                task_list=task_pagiobj.page(task_pagiobj.num_pages)
            buff["page"]=task_list.number
            buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(),i.rule,"","",i.get_info(),i.owner ,i.ip]}  for i in task_list]
            return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
    elif getinfo.has_key("ip"):
        #检索
        ip=getinfo.get("ip")
        status=getinfo.get("status")
        owner=getinfo.get("owner")
        info=getinfo.get("fn")
        rows=getinfo.get("rows","15")
        page=getinfo.get("page","1")
        def handleparam(ip,status,info,owner):
            result=locals()
            if ip=='':
                del result["ip"]
            if owner=="" or owner==None:
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
        buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(),i.rule,"","",i.get_info(),i.owner  ,i.ip]} for  i in task_list]
        return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
        pass
    cronserve=CronServe.objects.all().order_by("ip")

    userinfo=User.objects.all().values("username")
    return  render_to_response("manage.html",locals(), context_instance=RequestContext(request))

@login_required
def  stopcron(request):
    "stop cron "
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    server=get_cron_serve()
    buff={}
    try:
        int(tid)
    except:
        buff["status"]=False
        buff["message"]="ID不合法！"
    try:
        cron= Task.objects.get(pk=int(tid))
    except:
        buff["status"]=False
        buff["message"]="此tid不存在"
    else:
        if cron.status==1:
            try:
                result=server.stopcron(int(tid))
                if isinstance(result,tuple):
                    buff["status"],buff["message"]=result
                else:
                    buff["status"]=True
                    buff["message"]="Success!已禁用此cron！"
            except Exception as e:
                buff["status"]=False
                buff["message"]=str(e)
        elif cron.status==-1:
            buff["status"],buff["message"]=True,"Success!已禁用此Cron!"
        else:
            buff["status"],buff["message"]=False,"Error,此task状态为%s,不可禁用！"%cron.get_status()
    return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def restartcron(request):
    "restart cron"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    server=get_cron_serve()
    buff={}
    try:
        cron=Task.objects.get(pk=int(tid))
    except:
        buff["status"]=False
        buff["message"]="此tid不存在！"
    else:
        if cron.status==-1:
            try:
                int(tid)
            except:
                buff["status"]=False
                buff["message"]="ID不合法"
            try:
                result=server.startcron(tid)
                if isinstance(result,tuple):
                    buff["status"],buff["message"]=result
                else:
                    buff["status"]=True
                    buff["message"]="Success!已启用此cron！"
            except Exception as e:
                buff["status"]=False
                buff["message"]=str(e)
        elif cron.status==1:
            buff["status"]=True
            buff["message"]="Success!"
        else:
            buff["status"]=False
            buff["message"]="此task状态为%s,不可启用！"%cron.get_status()
    return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def touchcron(request):
    "立刻执行cron"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    server=get_cron_serve()
    buff={}
    try:
        int(tid)
    except:
        buff["status"],buff["message"]=False,"tid不合法！"
    else:
        try:
            _cron=Task.objects.get(pk=int(tid))
        except ObjectDoesNotExist:
            buff["status"],buff["message"]=False,"Error! 此Cron不存在！请重试！"
        else:
            if _cron.status!=1:
                buff["status"]=False
                buff["message"]="此task状态为%s,不可触发！"%_cron.get_status()
            else:
                try:
                    result=server.runcron(tid)
                    if isinstance(result,tuple):
                        buff["status"],buff["message"]=result
                    else:
                        buff["status"]=True
                        buff["message"]="Success!已触发此cron！"
                except Exception as e:
                    buff["status"]=False
                    buff["message"]=str(e)
    return HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def removecron(request):
    "删除cron"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    server=get_cron_serve()
    buff={}
    try:
        int(tid)
    except:
        buff["status"],buff["message"]=False,"tid不合法！"
    else:
        try:
            task=Task.objects.get(pk=int(tid))
        except ObjectDoesNotExist:
            buff["status"],buff["message"]=True,"Success! 已删除此cron!"
        else:
            try:
                result=server.removecron(tid)
                if isinstance(result,tuple):
                    buff["status"],buff["message"]=result
                else:
                    buff["status"]=True
                    buff["message"]="Success!已删除此cron！"
            except Exception as e:
                buff["status"]=False
                buff["message"]=str(e)
    return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
@login_required
def runrecord(request):
    "cron  运行记录"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    page=getinfo.get("page",'1')
    rows=getinfo.get("rows","10")
    page,rows=int(page),int(rows)
    buff={}
    task=Task.objects.get(pk=int(tid))
    runlog=RunLog.objects.filter(tid=int(tid)).order_by("-rid")
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
def logsdetail(request):
    "查看运行日志的stdout stderr"
    getinfo=request.GET
    postinfo=request.POST
    rid=getinfo.get("rid")
    runlog=RunLog.objects.get(pk=int(rid))
    stdout=runlog.stdout
    stderr=runlog.stderror
    #return  HttpResponse(json.dumps({"stdout":stdout,"stderr":stderr},ensure_ascii=False,indent=True),mimetype="application/javascript")
    return  render_to_response("cron_run_log.html",locals(),context_instance=RequestContext(request))

@login_required
def crondetail(request):
    "或者这个cron的详细信息"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")

    tid=int(tid)
    cron=Task.objects.get(pk=tid)
    buff={"ip":cron.ip,"name":cron.name,"rule":cron.rule,
          "url":cron.svnpath,"version":cron.version,
          "svnuser":cron.svnuser,"svnpasswd":cron.svnpasswd,
          "fn":cron.info,"filename":cron.filename}
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")

@login_required
def modifycron(request):
    "更改cron信息"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    _ip=postinfo.get("ip")
    name=postinfo.get("name")
    rule=postinfo.get("rule")

    svnpath=postinfo.get("url").strip()
    version=postinfo.get("version")
    svnuser=postinfo.get("svnuser")
    svnpasswd=postinfo.get("svnpasswd")
    info=postinfo.get("fn")
    args=""
    filename=postinfo.get("filename")

    serve=get_cron_serve()
    buff={}
    try:
        task= Task.objects.get(pk=int(tid))
    except:
        buff["status"]=False
        buff["message"]="Error!无效tid!"
    else:
        ip=task.ip
        if ip!=_ip:
            buff["status"]=False
            buff["message"]="不允许修改IP！"
        elif  name!=task.name:
            buff["status"]=False
            buff["message"]="不允许修改计划任务名！"

        else:
            valid_result=valid_input(ip,name,rule,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if valid_result!=True:
                buff["status"],buff["message"]=valid_result
            else:
                if   version=="*":
                    versioninfo=get_svn_top_version(svnpath,svnuser,svnpasswd)
                    if versioninfo[0]==False:
                        buff["status"],buff["message"]=versioninfo
                    else:
                        version=versioninfo[1]
                if buff=={}:
                    result= serve.modifycron(tid,name,svnpath,str(version),svnuser,svnpasswd,rule,info,request.user.username,args,filename)
                    if result!=True:
                        buff["status"],buff["message"]=result
                    else:
                        buff["status"]=True
                        buff["message"]="Success!"
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")










