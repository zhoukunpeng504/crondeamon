#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/7/15.
# ---------------------------------

from django.contrib.auth.models import User
def   valid_add_input(request):
    postinfo=request.POST
    username=postinfo.get("username")
    passwd=postinfo.get("pwd")
    confirm_passwd=postinfo.get("confirm_pwd")
    usergroupid=postinfo.get("usergroup")
    if  not  request.user.is_superuser:
        return  False,"您无权操作"
    if  username=="":
        return False,"请输入合法用户名"
    if User.objects.filter(username=username).count()!=0:
        return False,"该用户已存在"
    if passwd=='':
        return False,"请输入合法的密码"
    if len(passwd)<6:
        return  False,"密码必须大于6位"
    if  confirm_passwd!=passwd:
        return  False,"两次输入密码并不一致"
    user=User(username=username)
    user.set_password(passwd)
    user.save()
    return True