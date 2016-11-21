#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/15.
# ---------------------------------
from django.conf.urls import  include ,url,patterns

class Task(object):
    def __init__(self,name="task",app_name="task"):
        self.name=name
        self.app_name=app_name
    def get_urls(self):
        return  patterns("cap.task",
                         url(r"^$","views.home"),
                         url(r"^add/$","views.add"),
                         url(r"^manage/$","views.manage"),
                         url(r"^taskdetail/$","views.taskdetail"),  #task详情
                         url(r"^modifytask/$","views.modifytask"),    #修改task
                         url(r"^stoptask/$","views.stoptask"),       #停止task
                         url(r"^starttask/$","views.starttask"),     #开始task
                         url(r"^restarttask/$","views.restarttask")  ,#重启task
                         url(r"^removetask/$","views.removetask")   ,  #删除task
                         url(r"^logsdetail/$","views.logdetail")  ,     #运行Log
                         url(r"^runrecord/$","views.runrecord")
        )
    @property
    def urls(self):
        return self.get_urls(),self.app_name,self.name
    @urls.setter
    def urls(self,value):
        pass
    @urls.deleter
    def urls(self):
        pass
site=Task()