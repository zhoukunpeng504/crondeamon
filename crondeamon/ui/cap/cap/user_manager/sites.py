__author__ = 'Administrator'
from django.conf.urls import  include ,url,patterns

class Blog(object):
    def __init__(self,name="sytest",app_name="sytest"):
        self.name=name
        self.app_name=app_name
    def get_urls(self):
        return patterns("cap.user_manager",
                        url(r"^user_add/$", "views.add"),
                        url(r"^user_list/$", "views.list"),
                        url(r"^delete/$","views.delete"),
                        url(r"^info/$","views.info"),
                        url(r"change/$","views.change"),


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
site=Blog()