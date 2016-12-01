#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/11.
# ---------------------------------
import  MySQLdb

# create  table sql list
create_table_sql_list=[
                       '''CREATE TABLE if not EXISTS `cron_cronserve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` char(15) NOT NULL,
  `path` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`),
  KEY `cron_cronserve_49a8a8f2` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8 ''',


                       '''CREATE TABLE  if not EXISTS `cron_task` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `ip` char(15) NOT NULL,
  `addtime` int(11) NOT NULL,
  `edittime` int(11) NOT NULL DEFAULT '0',
  `rule` varchar(50) NOT NULL,
  `status` int(11) NOT NULL,
  `svnpath` varchar(1000) NOT NULL,
  `version` bigint(20) unsigned NOT NULL DEFAULT '0',
  `svnuser` varchar(30) NOT NULL,
  `svnpasswd` varchar(50) NOT NULL,
  `info` varchar(300) NOT NULL,
  `owner` varchar(300) NOT NULL,
  `args` varchar(500) NOT NULL,
  `filename` varchar(500) NOT NULL,
  PRIMARY KEY (`tid`),
  KEY `cron_task_52094d6e` (`name`),
  KEY `cron_task_49a8a8f2` (`ip`),
  KEY `owner` (`owner`(255)),
  KEY `owner_2` (`owner`(255)),
  KEY `project` (`project`)
) ENGINE=InnoDB AUTO_INCREMENT=1427 DEFAULT CHARSET=utf8''',


                 '''CREATE TABLE  if not EXISTS  `cron_runlog` (
  `rid` int(11) NOT NULL AUTO_INCREMENT,
  `tid` int(11) NOT NULL,
  `svnpath` varchar(100) NOT NULL,
  `version` bigint(20) unsigned NOT NULL DEFAULT '0',
  `crontime` int(11) NOT NULL,
  `begintime` int(11) NOT NULL,
  `endtime` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `stderror` longtext NOT NULL,
  `stdout` longtext NOT NULL,
  `type` int(3) NOT NULL DEFAULT '0',
  PRIMARY KEY (`rid`),
  KEY `cron_runlog_1fc17dc5` (`tid`),
  KEY `status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=10917677 DEFAULT CHARSET=utf8''',

                       '''CREATE TABLE if not EXISTS `task_task` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `ip` char(15) NOT NULL,
  `addtime` int(11) NOT NULL,
  `edittime` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `svnpath` varchar(500) NOT NULL,
  `version` bigint(20) unsigned NOT NULL DEFAULT '0',
  `svnuser` varchar(30) NOT NULL,
  `svnpasswd` varchar(50) NOT NULL,
  `info` varchar(500) NOT NULL,
  `owner` varchar(200) NOT NULL,
  `type` smallint(6) NOT NULL,
  `args` varchar(500) NOT NULL,
  `filename` varchar(500) NOT NULL,
  PRIMARY KEY (`tid`),
  KEY `task_task_52094d6e` (`name`),
  KEY `task_task_49a8a8f2` (`ip`),
  KEY `task_task_4741fd1b` (`owner`),
  KEY `project` (`project`)
) ENGINE=InnoDB AUTO_INCREMENT=1792 DEFAULT CHARSET=utf8''',
            ]
def valid(host,port,db,user,passwd):
    conn=MySQLdb.connect(host=host,port=port,user=user,db=db,passwd=passwd)
    cursor=conn.cursor()
    for i in create_table_sql_list:
        cursor.execute(i)
    cursor.close()
    conn.close()

def add_server(host,port,db,user,passwd,ip):
    conn=MySQLdb.connect(host=host,port=port,user=user,db=db,passwd=passwd)
    cursor=conn.cursor()
    cursor.execute("insert ignore into cron_cronserve(ip,path) VALUES(%s,%s)",(ip,"."))
    conn.commit()
    cursor.close()
    conn.close()
