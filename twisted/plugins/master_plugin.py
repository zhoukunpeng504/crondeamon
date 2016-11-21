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
import  ConfigParser
from crondeamon.common.valid_mysql import valid


class Options(usage.Options):

    optParameters = [
        ]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "crondeamon-master"
    description = "crondeamon-master"
    options=Options
    def makeService(self, options):
        cfg=ConfigParser.ConfigParser()
        result=cfg.read("/etc/crondeamon/master.ini")
        try:
            assert  result== ["/etc/crondeamon/master.ini"]
            assert cfg.sections()==["crondeamon"]
            config=dict(cfg.items("crondeamon"))
            host=config["host"]
            mysqlhost=config["mysqlhost"]
            mysqlport=int(config["mysqlport"])
            mysqldb=config["mysqldb"]
            mysqluser=config["user"]
            mysqlpasswd=config["passwd"]
            mysqlcharset=config["charset"]
        except:
            raise Exception("Config File /etc/crondeamon/master.ini is error please recheck it!")
        else:
            valid(mysqlhost,mysqlport,mysqldb,mysqluser,mysqlpasswd)
            from  crondeamon.master import service
            serverfactory = server.Site(service.MainRpc())
            return TCPServer(8017,serverfactory,interface=host)
serviceMaker = MyServiceMaker()