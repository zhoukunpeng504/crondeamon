#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/11.
# ---------------------------------
from warnings import filterwarnings
import MySQLdb
filterwarnings('ignore', category = MySQLdb.Warning)
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
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8; ''',


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
  KEY `owner` (`owner`(255))
) ENGINE=InnoDB AUTO_INCREMENT=1427 DEFAULT CHARSET=utf8 ;''',


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
) ENGINE=InnoDB AUTO_INCREMENT=10917677 DEFAULT CHARSET=utf8 ;''',

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
  `args` varchar(500) NOT NULL,
  `filename` varchar(500) NOT NULL,
  PRIMARY KEY (`tid`),
  KEY `task_task_52094d6e` (`name`),
  KEY `task_task_49a8a8f2` (`ip`),
  KEY `task_task_4741fd1b` (`owner`)
) ENGINE=InnoDB AUTO_INCREMENT=1792 DEFAULT CHARSET=utf8 ;''',
    '''CREATE TABLE if not EXISTS `task_runlog` (
  `rid` int(11) NOT NULL AUTO_INCREMENT,
  `tid` int(11) NOT NULL,
  `svnpath` varchar(100) NOT NULL,
  `version` int(11) NOT NULL,
  `crontime` int(11) NOT NULL,
  `begintime` int(11) NOT NULL,
  `endtime` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `stderror` longtext NOT NULL,
  `stdout` longtext NOT NULL,
  `type` smallint(6) NOT NULL,
  PRIMARY KEY (`rid`),
  KEY `task_runlog_e03e823b` (`tid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8''',
            '''CREATE TABLE  if not EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
)  ;''',



    '''CREATE TABLE  if not EXISTS  `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;''',


    '''CREATE TABLE if not EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_e4470c6e` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8; ''',



    '''CREATE TABLE if not EXISTS `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_bda51c3c` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_a7792de1` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',

'''CREATE TABLE if not EXISTS `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;''',


    '''CREATE TABLE if not EXISTS `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_fbfc09f1` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_f2045483` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE  if not EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_fbfc09f1` (`user_id`),
  KEY `django_admin_log_e4470c6e` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE if not EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_c25c2c28` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE if not EXISTS  `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;''',

    '''
INSERT ignore  INTO auth_user (id,username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) VALUES (1,'admin', '', '', '18749679769@163.com', 'pbkdf2_sha256$10000$qU64hbIvUFtx$WpemqR8eBDeTqR483ujW3KJXpxB3xMkDxOitPvMPFT0=', 1, 1, 1, '2017-03-09 15:01:47', '2017-02-20 10:46:14'),
 (2,'root', '', '', '', 'pbkdf2_sha256$10000$qwddQoKttd9q$vT2syIir6wJFvWOsHXq9tu85fFIFHIYFaAqm7k6v2HY=', 1, 1, 1, '2017-03-09 15:02:26', '2017-03-09 15:02:04');''',

   '''INSERT ignore   INTO django_content_type (id,name, app_label, model) VALUES
   (1,'permission', 'auth', 'permission'),
(2,'group', 'auth', 'group'),
(3,'user', 'auth', 'user'),
(4,'content type', 'contenttypes', 'contenttype'),
(5,'session', 'sessions', 'session'),
(6,'site', 'sites', 'site'),
(7,'log entry', 'admin', 'logentry'),
(8,'crondeamon宿主服务器', 'cron', 'cronserve'),
(9,'计划任务', 'cron', 'task'),
(10,'运行日志', 'cron', 'runlog'),
(11,'后台任务', 'task', 'task'),
(12,'运行日志', 'task', 'runlog');''',


            '''INSERT ignore  INTO auth_permission (id, name, content_type_id, codename) VALUES
(1, 'Can add permission', 1, 'add_permission'),
 (2, 'Can change permission', 1, 'change_permission'),
  (3, 'Can delete permission', 1, 'delete_permission'),
 (4, 'Can add group', 2, 'add_group'),
  (5, 'Can change group', 2, 'change_group') ,
 (6, 'Can delete group', 2, 'delete_group') ,
 (7, 'Can add user', 3, 'add_user') ,
 (8, 'Can change user', 3, 'change_user') ,
 (9, 'Can delete user', 3, 'delete_user') ,
 (10, 'Can add content type', 4, 'add_contenttype') ,
 (11, 'Can change content type', 4, 'change_contenttype') ,
 (12, 'Can delete content type', 4, 'delete_contenttype') ,
 (13, 'Can add session', 5, 'add_session') ,
 (14, 'Can change session', 5, 'change_session') ,
 (15, 'Can delete session', 5, 'delete_session') ,
 (16, 'Can add site', 6, 'add_site') ,
 (17, 'Can change site', 6, 'change_site') ,
 (18, 'Can delete site', 6, 'delete_site') ,
 (19, 'Can add log entry', 7, 'add_logentry') ,
 (20, 'Can change log entry', 7, 'change_logentry') ,
 (21, 'Can delete log entry', 7, 'delete_logentry') ,
 (22, 'Can add crondeamon宿主服务器', 8, 'add_cronserve') ,
 (23, 'Can change crondeamon宿主服务器', 8, 'change_cronserve') ,
 (24, 'Can delete crondeamon宿主服务器', 8, 'delete_cronserve') ,
 (25, 'Can add 计划任务', 9, 'add_task') ,
 (26, 'Can change 计划任务', 9, 'change_task') ,
 (27, 'Can delete 计划任务', 9, 'delete_task') ,
 (28, 'Can add 运行日志', 10, 'add_runlog') ,
 (29, 'Can change 运行日志', 10, 'change_runlog') ,
 (30, 'Can delete 运行日志', 10, 'delete_runlog') ,
 (31, 'Can add 后台任务', 11, 'add_task') ,
 (32, 'Can change 后台任务', 11, 'change_task') ,
 (33, 'Can delete 后台任务', 11, 'delete_task') ,
 (34, 'Can add 运行日志', 12, 'add_runlog') ,
 (35, 'Can change 运行日志', 12, 'change_runlog') ,
 (36, 'Can delete 运行日志', 12, 'delete_runlog');''',
    '''insert ignore into django_site values(1,"example.com","example.com");'''
]
def valid(host,port,db,user,passwd):
    for i in create_table_sql_list:
        conn = MySQLdb.connect(host=host, port=port, user=user, db=db, passwd=passwd, charset="utf8")
        cursor = conn.cursor()
        try:
            cursor.execute(i)
        except Exception as e :
            print i ,str(e),"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        cursor.close()
        conn.commit()
        conn.close()

def add_server(host,port,db,user,passwd,ip):
    conn=MySQLdb.connect(host=host,port=port,user=user,db=db,passwd=passwd)
    cursor=conn.cursor()
    cursor.execute("insert ignore into cron_cronserve(ip,path) VALUES(%s,%s)",(ip,"."))
    conn.commit()
    cursor.close()
    conn.close()
