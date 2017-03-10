============
crondeamon
============
***************
1.介绍
***************
crondeamon是用来管理计划任务及后台任务的项目， 其功能相当于supervisor+crontab，  基于twisted   django 框架。

***************
2.依赖
***************
python版本要求：

python>=2.6.x 

pip   svn   git


***************
3.安装
***************
pip install crondeamon

***************
4.运行
***************
192.168.8.94：
 ::

  [root@hadoop94 /]# pip install  git+git://github.com/zhoukunpeng504/crondeamon.git
  [root@hadoop94 /]# vim /etc/crondeamon/slave.ini                                                                                                          
  [crondeamon]
  host = 192.168.8.94
  mysqlhost = 192.168.15.34
  mysqlport = 3306
  mysqldb = crondeamon
  user = zhou
  passwd = zhou                                                                                                            
  charset = utf8

  [root@hadoop94 /]# python -m crondeamon.sbin.slave -c start
  /usr/local/lib/python2.7/site-packages/crondeamon/common/valid_mysql.py:112: Warning: Duplicate index 'owner_2' defined on the table 'crondeamon.cron_task'. This is deprecated and will be disallowed in a future release.
  cursor.execute(i)
  start success!
  [root@hadoop94 /]# ps aux|grep twistd
  root     31664  0.0  0.3 475548 20116 ?        Sl   09:56   0:00 /usr/local/bin/python2.7 /usr/local/bin/twistd --pidfile /data/crondeamon/slave/pid/crondeamon-slave.pid --logfile /data/crondeamon/slave/log/crondeamon-slave.log crondeamon-slave
  root     31697  0.0  0.0 103248   892 pts/0    S+   09:56   0:00 grep twistd

192.168.8.95:
::

  [root@hadoop95 ~]# pip install  git+git://github.com/zhoukunpeng504/crondeamon.git
  [root@hadoop95 ~]# mkdir /etc/crondeamon
  [root@hadoop95 ~]# vim  /etc/crondeamon/slave.ini
  [crondeamon]
  host=192.168.8.95                                                                                                        
  mysqlhost = 192.168.15.34
  mysqlport = 3306
  mysqldb = crondeamon
  user = zhou
  passwd = zhou
  charset = utf8 
  [root@hadoop95 ~]# python -m crondeamon.sbin.slave -c start
  start success!
192.168.8.96:
 ::

  [root@hadoop96 ~]# pip install  git+git://github.com/zhoukunpeng504/crondeamon.git
  [root@hadoop96 ~]# vim /etc/crondeamon/slave.ini

  [crondeamon]
  host=192.168.8.96                                                                                                        
  mysqlhost = 192.168.15.34
  mysqlport = 3306
  mysqldb = crondeamon
  user = zhou
  passwd = zhou
  charset = utf8
  [root@hadoop96 ~]# python -m crondeamon.sbin.slave -c start 

master安装：
192.168.8.94
 ::

  [root@hadoop94 /]# vim /etc/crondeamon/master.ini
  [crondeamon]
  host=192.168.8.94
  mysqlhost = 192.168.15.34
  mysqlport = 3306
  mysqldb = crondeamon
  user = zhou
  passwd = zhou
  charset = utf8
  [root@hadoop94 /]# python -m crondeamon.sbin.master -c start
  start success!
ui安装：
ui部分是基于django的，第一次启动ui时需要先syncdb，   syncdb过程中需要创建一个超级用户， 按照提示输入即可，该用户用于第一次登录系统。

192.168.8.94
 ::

  [root@hadoop94 /]# python -m crondeamon.ui.cap.manage  syncdb 
  [root@hadoop94 /]# python -m crondeamon.ui.cap.manage  runserver   0.0.0.0:8035
  Validating models...

  0 errors found
  Django version 1.4.16, using settings 'cap.settings'
  Development server is running at http://0.0.0.0:8035/
  Quit the server with CONTROL-C.
  
  