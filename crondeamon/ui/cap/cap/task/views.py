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
from cap.cron.models import  CronServe,App
from cap.models import  Project
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
            buff["rows"]=[{"cell":[i.tid,i.name,i.get_status(),[i.running,i.count],i.project,i.app,i.get_info() ,i.get_owner_and_type(),i.ip]}  for i in task_list]
        elif datatype=="add":
            u"增加一个Task"
            ip=postinfo.get("ip")
            ip_list=postinfo.getlist("ip")
            name=postinfo.get("name")
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
            '''if version=="*":
                svninfo=get_svn_top_version(svnpath,svnuser,svnpasswd)
                if svninfo[0]==False:
                    buff["status"],buff["message"]=svninfo
                else:
                    version=svninfo[1]'''
            if vcs==1:
                branch=''
            if vcs==2:
                try:
                    version=version[:10]
                    version=int(version,16)
                except:
                    pass
            valid_result= valid_input(ip,_type,name,project,app,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if valid_result!=True:
                buff["status"],buff["message"]=valid_result
            elif   vcs==2 and  branch == ""  :
                buff["status"],buff["message"]=(False,u"请输入分支！")
            elif vcs==2  and  version=="*":
                buff["status"],buff["message"]=(False,u"请输入正确的版本号！")
            else:
                num=int(name[-1])  if (len(name)>=3 and  name[:-1].endswith("*") and 49<=ord(name[-1])<=57) else 1
                if len(name)>=3 and name[-2]=="*" and 49<=ord(name[-1])<=57:
                    name=name[:-2]
                if version=="*":
                    versioninfo=get_svn_top_version(svnurl=svnpath,svnuser=svnuser,svnpasswd=svnpasswd)
                    if versioninfo[0]==False:
                        buff["status"],buff["message"]=versioninfo
                    else:
                        version=versioninfo[1]
                if buff=={}:
                    serve=get_task_serve()
                    try:
                        if  len(ip_list)==1:
                            result=serve.adddaemon(ip,name,project,app,svnpath,str(version),svnuser,svnpasswd,info,request.user.username,_type,args,filename,custom,num,branch)
                            if True in result:
                                buff["status"],buff["message"]= True,u"共成功%s个,共失败%s个"%(result.count(True),result.count(False))
                            else:
                                buff["status"],buff["message"]=False,u"创建失败！请稍后再试！%s"%(str(result))
                        else:
                            result=serve.multiadddaemon(ip_list,name,project,app,svnpath,str(version),svnuser,svnpasswd,info,request.user.username,_type,args,filename,custom,num,branch)
                            failedip=""
                            # for i,j  in  zip(ip_list,result):
                            #     if j ==False:
                            #         if failedip=="":
                            #             failedip+=i
                            #         else:
                            #             failedip+="、%s"%i
                            for i ,j in enumerate(ip_list):
                                if False in  result[i::len(ip_list)]:
                                    if failedip =="":
                                        failedip+=u"%s(%s个)"%(j,result[i::len(ip_list)].count(False))
                                    else:
                                        failedip+=u"、%s(%s个)"%(j,result[i::len(ip_list)].count(False))
                            buff["status"]=True
                            buff["message"]=u"共成功%s个，共失败%s个(%s)！"%(result.count(True),result.count(False),failedip)
                    except Exception as e:
                        buff["status"],buff["message"]=False,str(e)
        return HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")

    cronserve=CronServe.objects.all().values()
    cronproj=Project.objects.filter(~Q(name=u"空"))
    appinfo=[]
    for i in cronproj:
        cronapp=App.objects.filter(project=i).values("name")
        for j in cronapp:
            appinfo.append({"proj":i.name,"app":j["name"]})
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
            buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(),[i.running,i.count],i.project,i.app,i.get_info() ,i.get_owner_and_type(),i.ip]}  for i in task_list]
            return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")
    elif getinfo.has_key("project"):
        ip=getinfo.get("ip")
        project=getinfo.get("project")
        app=getinfo.get("app")
        status=getinfo.get("status")
        _type=getinfo.get("lan")
        info=getinfo.get("fn")
        owner=getinfo.get("owner")
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
            if owner=='' or owner==None:
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
        buff["rows"]=[{"cell":[i.tid,i.get_name(),i.get_status(), [i.running, i.count],i.project,i.app,i.get_info(),i.get_owner_and_type() ,i.ip]} for  i in task_list]
        return  HttpResponse(json.dumps(buff,ensure_ascii=False),mimetype="application/javascript")


    cronserve=CronServe.objects.all().order_by("ip")
    cronproj=Project.objects.filter(~Q(name="空"))
    appinfo=[]
    for i in cronproj:
        cronapp=App.objects.filter(project=i).values("name")
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
        buff={"ip":task.ip,"type":task.type,"name":task.name,"project":task.project,"app":task.app,"url":task.svnpath,"version":task.realversion,"branch":task.branch,
              "vcs":task.vcs,
              "svnuser":task.svnuser,"svnpasswd":task.svnpasswd,"args":task.args,"fn":task.info,"filename":task.filename,"custom":task.custom}
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
        elif app!=task.app or project !=task.project:
            buff=generate_dict(False,"不允许修改所属项目/应用！")
        elif len(ip_list)>1:
            buff=generate_dict(False,"不可选择多台主机！")
        elif vcs!=task.vcs:
            buff=generate_dict(False,"不可修改版本控制方式！")
        else:
            result=valid_input(ip,_type,name,project,app,svnpath,version,svnuser,svnpasswd,info,args,filename)
            if result!=True:
                buff=generate_dict(*result)
            elif   vcs==2 and  branch == ""  :
                result=generate_dict(False,"请输入分支！")
            elif vcs==2  and  version=="*":
                result=generate_dict(False,"请输入正确的版本号！")
            else:
                if version=="*":
                    versioninfo=get_svn_top_version(svnpath,svnuser,svnpasswd)
                    if versioninfo[0]==False:
                        buff=generate_dict(versioninfo[0],versioninfo[1])
                    else:
                        version=versioninfo[1]
                if  not  locals().has_key("buff"):
                    result= run_serve_fun("modifydaemon",ip,task.tid,name,project,app,svnpath,str(version),svnuser,svnpasswd,info,_type,args,filename,custom,branch)
                    if result==True:
                        buff=generate_dict(True,"Success!")
                    else:
                        buff=generate_dict(*result)
    return  HttpResponse(json.dumps(buff,ensure_ascii=False,indent=True),mimetype="application/javascript")



