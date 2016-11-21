#coding:utf-8
__author__ = 'Administrator'
from django.http import  HttpResponse, HttpResponseRedirect
from django.shortcuts import  render_to_response
from django.utils import  simplejson
from django.core.paginator import Paginator
from django.utils.log  import  mail
from django.template import  Context,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import  csrf_exempt
from utils import  status
#---------------主页-----------------
@login_required
def home(request):
    return HttpResponseRedirect("/cron/")


@login_required
def changepwd(request,template_name):
    "更改密码"
    oldpwd=request.POST.get("oldpwd",'')
    newpwd=request.POST.get('newpwd','')
    confirm_pwd=request.POST.get('confirm_pwd','')
    username=request.user.username
    def valid_input(oldpwd, newpwd,confirpwd):
        if not  request.user.check_password(oldpwd):
            return False,"您输入的旧密码错误！请重试"
        if newpwd==confirpwd:
            return True
        else:
            return False,"两次输入不一致！请重试！"
    if newpwd==confirm_pwd==oldpwd and newpwd=="" :
        return  render_to_response("change_pwd.html",context_instance=RequestContext(request))
    else:
        result=valid_input(oldpwd, newpwd,confirpwd=confirm_pwd)
        if result==True:
            user=User.objects.get(username=username)
            user.set_password(newpwd)
            user.save()
            return status(request,message="Success! 密码修改成功！")
        else:
            return status(request,message="Error! %s"%result[1])
@login_required
def mainjs(request):
    return  HttpResponseRedirect('/static/main.js')



