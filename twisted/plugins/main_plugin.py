# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/7/20.
# ---------------------------------
from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker,MultiService
from twisted.application.internet import TCPServer
import  sys
from crondeamon.common.valid_configfile import valid_config
from twisted.internet import reactor, protocol
from twisted.web.wsgi import WSGIResource
from twisted.web import  server
import os
from crondeamon.ui import cap

reload(sys)
sys.setdefaultencoding("utf-8")

def get_manage_dir():
    return  cap.__path__
sys.path.append(get_manage_dir()[0])


class Options(usage.Options):

    optParameters = [
        ]

class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "crondeamon"
    description = "crondeamon"
    options=Options
    def makeService(self, options):
        config=valid_config()
        s=MultiService()
        from  crondeamon.slave import  service as subrpc
        serverfactory = server.Site(subrpc.MainRpc())
        slave_service=TCPServer(int(config["slaveport"]),serverfactory,interface=config["host"])
        slave_service.setServiceParent(s)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cap.settings")
        from django.core.handlers.wsgi import WSGIHandler
        application = WSGIHandler()
        resource = WSGIResource(reactor, reactor.getThreadPool(), application)
        ui_service=TCPServer(int(config["uiport"]),server.Site(resource),interface=config["host"])
        ui_service.setServiceParent(s)
        return  s

serviceMaker = MyServiceMaker()