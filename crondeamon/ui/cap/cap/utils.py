#coding:utf-8
__author__ = 'Administrator'
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import  render_to_response
from  django.template import RequestContext
from django.http import  HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import Group
import  socket
import  os
import  urllib
def  sendrtx(title,message,*args):
    for name in args:
        try:
            if type(title)==unicode:
                title=title.encode("utf-8")
            if type(message)==unicode:
                message=message.encode("utf-8")
            url="http://oa.gongchang.cn/sendtortx.php?receiver=%s&notifytitle"\
                "=%s&notifymsg=%s"%(name,title,message)
            urllib.urlopen(url)
        except Exception as e :
            pass
def range_list_of(page_object):
    num_pages = page_object.paginator.num_pages
    if num_pages <= 5:
        range_list = range(1, num_pages+1)
    else:
        if page_object.number < 3:
            range_list = range(1,6)
        elif page_object.number > (num_pages-2):
            range_list = range(num_pages-4, num_pages+1)
        else:
            range_list = range(page_object.number-2, page_object.number+3)
    return range_list
def encrypt(key, s):
    b = bytearray(str(s).encode("gbk"))
    n = len(b) # 求出 b 的字节数
    c = bytearray(n*2)
    j = 0
    for i in range(0, n):
        b1 = b[i]
        b2 = b1 ^ key # b1 = b2^ key
        c1 = b2 % 16
        c2 = b2 // 16 # b2 = c2*16 + c1
        c1 = c1 + 65
        c2 = c2 + 65 #
        c[j] = c1
        c[j+1] = c2
        j = j+2
    return c.decode("gbk")

def decrypt(key, s):
    c = bytearray(str(s).encode("gbk"))
    n = len(c) # 计算 b 的字节数
    if n % 2 != 0 :
        return ""
    n = n // 2
    b = bytearray(n)
    j = 0
    for i in range(0, n):
        c1 = c[j]
        c2 = c[j+1]
        j = j+2
        c1 = c1 - 65
        c2 = c2 - 65
        b2 = c2*16 + c1
        b1 = b2^ key
        b[i]= b1
    try:
        return b.decode("gbk")
    except:
        return "failed"


def my_pagination(request, queryset, display_amount=18, after_range_num = 5,bevor_range_num = 4):
    paginator = Paginator(queryset, display_amount)
    try:
        page = int(request.GET.get('page'))
    except:
        page = 1
    try:
        objects = paginator.page(page)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    except:
        objects = paginator.page(1)
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range = paginator.page_range[0:page+bevor_range_num]
    return objects, page_range
def status(request,message):
    "状态"
    return render_to_response("status.html",locals(),context_instance=RequestContext(request))


# 分页函数
def my_paginator(request,list,page_size=10):
    page = int(request.GET.get('page',1))

    paginatior=Paginator(list,page_size)
    try:
        cur_page_obj=paginatior.page(page)
    except EmptyPage:
        #如果是空页就最大页paginatior.num_pages
        cur_page_obj=paginatior.page(paginatior.num_pages)
    #小于5页全显示
    if paginatior.num_pages<=5:
        page_range=paginatior.page_range
    else:
        #大于5页显示，且在后5页，显示后5页
        if page>paginatior.num_pages-5:
            page_range=paginatior.page_range[-5:]
        #前两页显示前5页
        elif page<=2:
            page_range=paginatior.page_range[:5]
        #中间页
        else:
           page_range=paginatior.page_range[page-2:page+3]
    return cur_page_obj,page_range
import re
def validate_date(date_time):
    regex = r'(\d+)/(\d+)/(\d+)'
    pattern = re.compile(regex)
    m = pattern.match(date_time)
    if m:
        date_time = pattern.sub(r'\3-\1-\2', date_time)
    return date_time

def  supervisor_required(func):
    def wappedfun(request):
        if request.user.is_superuser:
            return func(request)
        else:
            return HttpResponse("/login/?next="+request.path)
    return wappedfun

def valid_group_required(*args):
    "验证用户组的装饰器，主要是用于限制视图函数的权限"
    def function(func):
        def wappedfun(request):
            grouplist=[Group.objects.get(name=i).name  for i in  args]
            request.user.valid_group_args=grouplist
            group=request.user.groups.all()[0].name
            request.user.group=group
            if (group  in grouplist) or group=="管理员" :
                return  func(request)
            else:
                return  HttpResponseRedirect("/login/?next="+request.path)
        return wappedfun
    return  function

def get_svn_top_version(svnurl,svnuser,svnpasswd):
    infoobject=os.popen("svn info %s --username %s --password %s --no-auth-cache --non-interactive"%(svnurl,svnuser,svnpasswd))
    result=infoobject.read()
    result=result.decode("utf-8")

    if result=='':
        return False,"无法获取%s的版本信息"%svnurl
    else:
        _u=re.search(ur"版本: (\d+)",result)
        if _u==None:
            _u=re.search(ur"Revision: (\d+)",result)
        return  True,int(_u.groups()[0])

def valid_exception(fun,*args):
    "验证一个函数执行是否异常"
    try:
        fun(*args)
    except:
        return False
    else:
        return True

class ValidObj(object):
    "对于一个元素验证的一个抽象"
    def __init__(self,request, method,element,valid,errormsg):
        self.request=request
        self.method=method
        self.element=element
        self.valid=valid
        self.errormsg=errormsg
    def valid_now(self):
        try:
            _u=getattr(self.request,self.method)[self.element]
        except:
            return False,self.errormsg
        else:
            if self.valid(_u)==False:
                return False,self.errormsg
            else:
                return True

def valid_common_handle(*args):
    "通用的验证输入的函数"
    for i in args:
        assert isinstance(i ,ValidObj)
    for i in args:
        result=i.valid_now()
        if result!=True:
            return  result
        else:
            pass
    return True

