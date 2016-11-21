#coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/1.
# ---------------------------------
from django.conf.urls import  include ,url,patterns

class Cron(object):
    def __init__(self,name="cron",app_name="cron"):
        self.name=name
        self.app_name=app_name
    def get_urls(self):
        return patterns("cap.cron",
                        url(r"^$","views.home"),                         #Home家目录
                        url(r"^test/$","views.test"),                    #test
                        url(r"^add/$","views.add"),
                        url(r"^manage/$","views.manage"),
                        url(r"^stopcron/","views.stopcron"),         #stop cron
                        url(r"^restartcron/","views.restartcron"),   #restart cron
                        url(r"^touchcron/","views.touchcron"),     #立刻执行cron
                        url(r"^removecron/","views.removecron")  ,  #删除cron
                        url(r"^runrecord/","views.runrecord"),  #运行记录
                        url(r"logsdetail/","views.logsdetail"),  #stdout stderr
                        url(r"^crondetail/$","views.crondetail"),
                        url(r"^modifycron/$","views.modifycron"),
# --------------------------------------------------------------

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
site=Cron()