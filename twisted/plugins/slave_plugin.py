# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/7/20.
# ---------------------------------
from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.web import  server
from twisted.application.internet import TCPServer
import  ConfigParser
from twisted.spread import pb
import  sys
from crondeamon.common.valid_configfile import valid_config



class Options(usage.Options):

    optParameters = [
        ]

class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "crondeamon-slave"
    description = "crondeamon-slave"
    options=Options
    def makeService(self, options):
        config=valid_config()
        from  crondeamon.slave import  service as subrpc
        serverfactory = server.Site(subrpc.MainRpc())
        return TCPServer(int(config["slaveport"]),serverfactory,interface=config["host"])

serviceMaker = MyServiceMaker()