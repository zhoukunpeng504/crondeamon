# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/30.
# ---------------------------------

from cap.models import Project
from cap.pub.models import App,Server,SvnServer,Decide,FileMode
from django.db.models import  ObjectDoesNotExist
import  os
_yes=Decide.objects.get(decision=True)
_no=Decide.objects.get(decision=False)
_mode_755=FileMode.objects.get(pk=3)
_mode_777=FileMode.objects.get(pk=4)
_svnserve=SvnServer.objects.get(pk=2)
_project=Project.objects.get(pk=3)
'''
def getserve(ip):
    try:
        serve=Server.objects.get(ip=ip)
    except ObjectDoesNotExist:
        serve=Server(ip=ip,user="cap",password="gccap2O15",group="www",ssh_port="2828")
        serve.save()
    return serve
for i in  a[1:] :
    print i
    _u=  __import__("cnapps.%s.deploy"%i,fromlist=["deploy"])
    print "import success!"
    globals()["deploy"]=_u
    try:
        App.objects.get(name=deploy.app_name)
    except ObjectDoesNotExist:
        print dir(App)
        app=App(name=deploy.app_name,  project=  _project,  source_svn=  "svn://192.168.8.168/%s"%deploy.app_name ,svn_server=     _svnserve,   deploy_to=  deploy.deploy_to,
                old_version_num= 10,  cmd_after_deploy=  "\n".join(deploy.after_deploy),
                formalfilemode= _mode_755     ,testfilemode= _mode_777, decide=   _no)
        app.save()
        formalsshinfo=    [ getserve(j.split(":")[0]) for j  in  getattr(deploy,"form_webs",["192.168.2.54:2828"])]
        testsshinfo= [ getserve(j.split(":")[0])  for j in deploy.test_webs]
        app.formalsshinfo=formalsshinfo
        app.testsshinfo=testsshinfo
        app.save()
    else:
        pass'''
apps=App.objects.filter(project=_project)
for i in apps:
    if "svn://192.168.8.168" in  i.source_svn:
        svnurl=i.source_svn
        newsvnurl= svnurl.replace("svn://192.168.8.168","svn://192.168.8.168:3690")
        i.source_svn=newsvnurl
        i.save()





