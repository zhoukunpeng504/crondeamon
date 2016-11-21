#coding:utf-8
__author__ = 'python'
from django.db import  models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django import  forms


# class ProfileBase(type):                    #对于传统类，他们的元类都是types.ClassType
#     def __new__(cls,name,bases,attrs):      #带参数的构造器，__new__一般用于设置不变数据类型的子类
#         module = attrs.pop('__module__')
#         parents = [b for b in bases if isinstance(b, ProfileBase)]
#         if parents:
#             fields = []
#             for obj_name, obj in attrs.items():
#                 if isinstance(obj, models.Field): fields.append(obj_name)
#                 User.add_to_class(obj_name, obj)
#             UserAdmin.fieldsets = list(UserAdmin.fieldsets)
#             UserAdmin.fieldsets.append((_(name), {'fields': fields}))
#             UserAdmin.fieldsets=tuple(UserAdmin.fieldsets)
#             UserAdmin.list_display=list(UserAdmin.list_display)
#             UserAdmin.list_display+=fields
#             UserAdmin.list_display=tuple(UserAdmin.list_display)
#             UserAdmin.add_fieldsets[0][1]["fields"]=tuple(list(UserAdmin.add_fieldsets[0][1]["fields"])+fields)
#         return super(ProfileBase, cls).__new__(cls, name, bases, attrs)
#
# class ProfileUser(object):
#     __metaclass__ = ProfileBase     #类属性
class Project(models.Model):
    name=models.CharField (_("项目名称") ,max_length=50,blank=False,unique=True)
    class Meta:
        verbose_name="项目"
        verbose_name_plural="所有项目"
    def __unicode__(self):
        return self.name

#
# class MyProfile(ProfileUser):
#
#     project=models.ManyToManyField(verbose_name="所属项目" , to= Project,null=False, blank=False)
