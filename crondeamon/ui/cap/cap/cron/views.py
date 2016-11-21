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
from models import   Task ,RunLog,CronServe,App
from cap.models import Project
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
            ip_list=postinfo.getlist("ip")
            name=postinfo.get("name")
            rule=postinfo.get("rule")
            project=postinfo.get("project")
            app=postinfo.get("app")
            svnpath=postinfo.get("url").strip()
            version=postinfo.get("version")
            svnuser=postinfo.get("svnuser")
            svnpasswd=postinfo.get("svnpasswd")
            info=postinfo.get("fn")
            _type=postinfo.get("type")
            args=postinfo.get("args")
            filename=postinfo.get("filename")
            custom=postinfo.get("custom")
            vcs=int(postinfo.get("vcs","1"))
            branch=postinfo.get("branch","")
            buff={}
            '''if version=="*"    :
                versioninfo=get_svn_top_version(svnurl=svnpath,svnuser=svnuser,svnpasswd=svnpasswd)
                if versioninfo[0]==False:
                    buff["status"],buff["message"]=versioninfo
                else:
                    version=versioninfo[1]'''
            if vcs==1:
                branch=''
            if vcs==2:
                try:
                    version=version[:10]
                    version=int(version,16)
                except:
                    pass
            valie_result=valid_input(ip if len(ip_list)==1 else ip_list ,_type,name,rule,project,app,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if  valie_result!=True:
                buff["status"],buff["message"]=valie_result
            elif   vcs==2 and  branch == ""  :
                buff["status"],buff["message"]=(False,"请输入分支！")
            elif vcs==2  and  version=="*":
                buff["status"],buff["message"]=(False,"请输入正确的版本号！")
            else:
                if version=="*":
                    versioninfo=get_svn_top_version(svnurl=svnpath,svnuser=svnuser,svnpasswd=svnpasswd)
                    if versioninfo[0]==False:
                        buff["status"],buff["message"]=versioninfo
                    else:
                        version=versioninfo[1]
                if buff=={}:
                    server=get_cron_serve()

                    if  len(ip_list)==1:
                        result=server.addcron(ip,name,project,app,svnpath,str(version),svnuser,svnpasswd,rule,info,request.user.username,int(_type),args,filename,custom,branch)
                        if result!=True:
                            buff["status"],buff["message"]=result
                        else:
                            buff["status"]=True
                            buff["message"]="Success!"
                    else:
                        result=server.multiaddcron(ip_list,name,project,app,svnpath,str(version),svnuser,svnpasswd,rule,info,request.user.username,int(_type),args,filename,custom,branch)

                        failedip=""
                        for i,j  in  zip(ip_list,result):
                            if j ==False:
                                if failedip=="":
                                    failedip+=i
                                else:
                                    failedip+="、%s"%i
                        buff["status"]=True
                        buff["message"]="成功%s个，失败%s个(%s)！"%(result.count(True),result.count(False),failedip)
        elif datatype=="proj":
            projectname=getinfo.get("project")
            appinfo=[]
            apps=App.objects.filter(project__name=projectname)
            for i in apps:
                appinfo.append(i.name)
            buff=appinfo
        return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
    else:
        cronserve=CronServe.objects.all().values()
        cronproj=Project.objects.filter(~Q(name="空"))
        appinfo=[]
        for i in cronproj:
            cronapp=App.objects.filter(project=i).values("name")
            for j in cronapp:
                appinfo.append({"proj":i.name,"app":j["name"]})
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
            buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(),i.rule,i.project,i.app,i.get_info(),i.get_owner_and_type() ,i.ip]}  for i in task_list]
            return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
    elif getinfo.has_key("project"):
        #检索
        ip=getinfo.get("ip")
        project=getinfo.get("project")
        app=getinfo.get("app")
        status=getinfo.get("status")
        _type=getinfo.get("lan")
        owner=getinfo.get("owner")
        info=getinfo.get("fn")
        rows=getinfo.get("rows","15")
        page=getinfo.get("page","1")
        def handleparam(ip,project,app,status,type,info,owner):
            result=locals()
            if ip=='':
                del result["ip"]
            if project=='':
                del result["project"]
            if app=='':
                del result["app"]
            if owner=="" or owner==None:
                del result["owner"]
            try:
                int(status)
            except:
                del result["status"]
            try:
                int(type)
            except:
                del result["type"]
            if info=='':
                del result["info"]
            if result.has_key("info"):
                del  result["info"]
                result["info__icontains"]=info
            return  result
        args=handleparam(ip,project,app,status,_type,info,owner)
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
        buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(),i.rule,i.project,i.app,i.get_info(),i.get_owner_and_type() ,i.ip]} for  i in task_list]
        return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
        pass
    cronserve=CronServe.objects.all().order_by("ip")
    cronproj=Project.objects.filter(~Q(name="空"))
    appinfo=[]
    for i in cronproj:
        cronapp=App.objects.filter(project=i).order_by("-name").values("name")
        for j in cronapp:
            appinfo.append({"proj":i.name,"app":j["name"]})
    project_info={}
    for i in  appinfo:
        if not  project_info.has_key(i["proj"]):
            project_info[i["proj"]]=[i["app"]]
        else:
            project_info[i["proj"]].append(i["app"])

    for i in project_info:
        project_info[i]="   ".join(map(lambda k: '''<option value="%s">%s</option>'''%(k,k) ,project_info[i]))
    project_info['']=u"<option value=''>组</option>"+ "   ".join(project_info.values())
    for j in cronproj:
        if project_info.has_key(j.name):
            project_info[j.name]=u"<option value=''>组</option>"+project_info[j.name]
        else:
            project_info[j.name]=u"<option value=''>组</option>"
    project_info=json.dumps(project_info,ensure_ascii=False)
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
    buff={"ip":cron.ip,"name":cron.name,"rule":cron.rule,"project":cron.project,"app":cron.app,
          "url":cron.svnpath,"version":cron.realversion,"branch":cron.branch,"vcs":cron.vcs,
          "svnuser":cron.svnuser,"svnpasswd":cron.svnpasswd,
          "fn":cron.info,"type":cron.type,"args":cron.args,"filename":cron.filename,"custom":cron.custom}
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")

@login_required
def modifycron(request):
    "更改cron信息"
    getinfo=request.GET
    postinfo=request.POST
    tid=getinfo.get("tid")
    _ip=postinfo.get("ip")
    ip_list=postinfo.getlist("ip")
    name=postinfo.get("name")
    rule=postinfo.get("rule")
    project=postinfo.get("project")
    app=postinfo.get("app")
    svnpath=postinfo.get("url").strip()
    version=postinfo.get("version")
    svnuser=postinfo.get("svnuser")
    svnpasswd=postinfo.get("svnpasswd")
    info=postinfo.get("fn")
    _type=postinfo.get("type")
    args=postinfo.get("args")
    filename=postinfo.get("filename")
    custom=postinfo.get("custom")
    vcs=postinfo.get("vcs","1")
    vcs=int(vcs)
    branch=postinfo.get("branch","")
    if vcs==1:
        branch=''
    if vcs==2:
        try:
            version=version[:10]
            version=int(version,16)
        except:
            pass
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
        elif app!=task.app or project!=task.project:
            buff["status"]=False
            buff["message"]="不允许修改所属项目/应用！"
        elif len(ip_list)>1:
            buff["status"],buff["message"]=False,"不可选择多台主机！"
        elif vcs!=task.vcs:
            buff["status"],buff["message"]=(False,"不可修改版本控制方式！")
        else:
            valid_result=valid_input(ip,_type,name,rule,project,app,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if valid_result!=True:
                buff["status"],buff["message"]=valid_result
            elif   vcs==2 and  branch == ""  :
                buff["status"],buff["message"]=(False,"请输入分支！")
            elif vcs==2  and  version=="*":
                buff["status"],buff["message"]=(False,"请输入正确的版本号！")
            else:
                if   version=="*":
                    versioninfo=get_svn_top_version(svnpath,svnuser,svnpasswd)
                    if versioninfo[0]==False:
                        buff["status"],buff["message"]=versioninfo
                    else:
                        version=versioninfo[1]
                if buff=={}:
                    result= serve.modifycron(ip,tid,name,project,app,svnpath,str(version),svnuser,svnpasswd,rule,info,request.user.username,int(_type),args,filename,custom,branch)
                    if result!=True:
                        buff["status"],buff["message"]=result
                    else:
                        buff["status"]=True
                        buff["message"]="Success!"
            #buff={"status":True,"message":"Success!!"}
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")










