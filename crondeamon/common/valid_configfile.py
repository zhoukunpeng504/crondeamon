# coding:utf-8

import ConfigParser
import MySQLdb
import os


def valid_config():
    cfg = ConfigParser.ConfigParser()
    try:
        result = cfg.read("/etc/crondeamon.ini")
        assert result == ["/etc/crondeamon.ini"]
    except:
        raise Exception(
            u'''Error！　未找到配置文件 /etc/crondeamon.ini !!，请新建配置文件
            请参照如下配置格式：
            [crondeamon]
            mysqlhost=192.168.15.34
            mysqlport=3306
            mysqldb=testabc
            user=root
            passwd=123456
            charset=utf8
            host=192.168.15.34
            datadir=/data/test/crondeamon
            slaveport=8023'''
        )
    try:
        assert cfg.sections() == ["crondeamon"]
        config = dict(cfg.items("crondeamon"))
    except:
        raise Exception(
            u'''Error! /etc/crondeamon.ini 中必须包含（且只包含）crondeamon区块！
            请参照如下配置格式：
            [crondeamon]
            mysqlhost=192.168.15.34
            mysqlport=3306
            mysqldb=testabc
            user=root
            passwd=123456
            charset=utf8
            host=192.168.15.34
            datadir=/data/test/crondeamon
            slaveport=8023'''
        )
    if config.has_key("host"):
        try:
            host = config["host"]
            assert host and host != "127.0.0.1" and host != "localhost"
        except:
            raise Exception(
                u'''Error！/etc/crondeamon.ini 中 host配置项错误，　host不能为127.0.0.1 或localhost
                '''
            )
    else:
        config["host"] = "0.0.0.0"
    try:
        mysqlhost = config["mysqlhost"]
        mysqlport = int(config["mysqlport"])
        mysqldb = config["mysqldb"]
        mysqluser = config["user"]
        mysqlpasswd = config["passwd"]
        mysqlcharset = config["charset"]
        conn = MySQLdb.connect(host=mysqlhost, port=mysqlport, db=mysqldb, user=mysqluser, passwd=mysqlpasswd,
                               charset=mysqlcharset)
        conn.close()
    except:
        raise Exception(
            u'''Error! /etc/crondeamon.ini 中 mysql配置项错误，连接mysql失败！''')
    if not config.has_key("datadir"):
        raise Exception("datadir尚未配置!")
    config["slaveport"] = 8023
    config["uiport"] = 8024
    return config
    # valid_config()
