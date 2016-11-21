#coding:utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import login,logout
from django.http import  HttpResponse,HttpResponseRedirect
import  cron
import  task
import  views
import user_manager
from cap import  settings
from django.views import  static
admin.autodiscover()
import  os
from django.views.static import serve,Http404
def tjconfig(request,path):
    try:
        return serve(request,path, os.path.join(settings.STATICFILES_DIRS[0],"tjconfig"),False)
    except  Http404 :
        return serve(request,"default.js", os.path.join(settings.STATICFILES_DIRS[0],"tjconfig"),False)


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cap.views.home', name='home'),
    # url(r'^cap/', include('cap.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r"^robots\.txt$",lambda request:HttpResponse("User-agent: *\nDisallow: /",mimetype="text/plain")),   #robots
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r"^login/$",login,{"template_name":"login.html"}),
    url(r"^logout/$",logout,{"next_page":"/"}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_DIRS[0], 'show_indexes': settings.DEBUG}),
    url(r'^tjconfig/(?P<path>.*)$', lambda request,path:HttpResponseRedirect("https://tj.gongchang.com%s"%request.get_full_path())),  #统计config js
    url(r"^changepwd/",views.changepwd,{"template_name":"change_pwd.html"}),#更改密码
    # Uncomment the next line to enable the admin:
    url(r"^$","cap.views.home"),                  #Home家目录
    url(r'^admin/', include(admin.site.urls)),    #admin页面
    url(r"^cron/",include(cron.site.urls)),       #cron 计划任务
    url(r"^task/",include(task.site.urls)),              #task后台任务

    url(r"user_manager/",include(user_manager.site.urls))   ,

)
