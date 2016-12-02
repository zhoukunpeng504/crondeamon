#coding:utf-8
__author__ = 'Administrator'
from django.shortcuts import render_to_response
from django import forms
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from cap.utils import my_pagination,validate_date
from django.db import connection
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import datetime,time,math
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import  Q
from cap.utils import status,supervisor_required,valid_group_required
from utils import  valid_add_input
from django.contrib.auth.models import  Group
@login_required
@supervisor_required
def add(request):
    "添加用户"

    if request.method=='POST':
        result=valid_add_input(request)
        if result!=True:
            return status(request,message="Error! %s"%result[1])
        else:
            return status(request,message="Success!")
    else:
        allgroup=Group.objects.all()
        return render_to_response('user_add.html',locals(), context_instance=RequestContext(request))

@login_required
@supervisor_required
def list(request):
    '''展示用户列表'''
    username= User.objects.all()
    usertype=request.POST.get('usertype','')
    proj_name=request.POST.get('proj_name','')
    a=int(request.GET.get('page','1'))
    allgroup = Group.objects.all()#获取所有组
    p=Paginator(username,10)
    try:
        contacts=p.page(a)
    except PageNotAnInteger:
        contacts = p.page(1)
    except EmptyPage:
        contacts = p.page(p.num_pages)
#    '''判断用户类型和所属行业是否同时存在'''
    if usertype and not proj_name:#筛选出某一用户组的用户列表
        user_group=Group.objects.get(name=usertype)
        username_list=User.objects.filter(groups=user_group)
    elif proj_name and not usertype:#筛选出某一项目类型的用户列表
        username_list=User.objects.filter(project=projects_name)
    elif usertype and proj_name:#筛选用户组和用户类型的联合查询
        user_group=Group.objects.get(name=usertype)
        username_list=User.objects.filter(groups=user_group,project=projects_name)
    else:
        username_list=p.page(a)
    for usernames in username_list:
        if usernames.is_superuser is True:
            usernames.usertype="admin"
        else:
            usernames.usertype="普通用户"

        if usernames.is_active is True:
            usernames.useractive = "有效用户"
        else:
            usernames.useractive = "无效用户"
    return render_to_response('user_list.html',locals(),context_instance=RequestContext(request))

@login_required
@supervisor_required
def delete(request):
    "删除用户"
    getinfo=request.GET
    id=getinfo.get("id")
    assert  id!=None
    queryset=User.objects.filter(pk=int(id))
    if queryset.count()==0:
        message="Error!该用户已不存在！"
    else:
        _user=queryset[0]
        _user.project=[]
        _user.delete()
        message="Success!成功删除%s！"%_user.username
    return HttpResponse(message,mimetype="application/javascript")




