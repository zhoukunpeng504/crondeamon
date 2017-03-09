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



class Options(usage.Options):

    optParameters = [
        ]

class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "crondeamon-slave"
    description = "crondeamon-slave"
    options=Options
    def makeService(self, options):
        cfg=ConfigParser.ConfigParser()
        result=cfg.read("/etc/crondeamon.ini")
        try:
            assert  result== ["/etc/crondeamon/slave.ini"]
            assert cfg.sections()==["crondeamon"]
            config=dict(cfg.items("crondeamon"))
            host=config["host"]
            assert  host  and host !="127.0.0.1"  and host !="localhost"
            mysqlhost=config["mysqlhost"]
            mysqlport=int(config["mysqlport"])
            mysqldb=config["mysqldb"]
            mysqluser=config["user"]
            mysqlpasswd=config["passwd"]
            mysqlcharset=config["charset"]
            slaveport=config["slaveport"]
        except:
            raise Exception("Config File /etc/crondeamon.ini is error please recheck it!")
        else:
            from  crondeamon.slave import  service as subrpc
            serverfactory = server.Site(subrpc.MainRpc())
            return TCPServer(slaveport,serverfactory,interface=host)

serviceMaker = MyServiceMaker()