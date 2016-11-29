============
crondeamon
============
***************
1.介绍
***************
crondeamon是用来管理计划任务及后台任务的项目， 其功能相当于supervisor+crontab，  基于twisted   django 框架。  crondeamon集群有三个角色：

1.slave  slave主要是用来控制进程的启动和销毁

2.master master主要是集中控制所有的slave节点

3.ui     ui主要是提供web界面

***************
2.依赖
***************
python版本要求：

python>=2.6.x 

pip

mysql

***************
3.安装
***************
三台机器，192.168.8.94   192.168.8.95  192.168.8.96   系统环境：centos 6   python版本：2.7.10  ， 数据库：host = 192.168.15.34  port = 3306  user = zhou   password =zhou  database = crondeamon 

角色规划：

slave:192.168.8.94 192.168.8.94  192.168.8.96 

master:192.168.8.94 

ui: 192.168.8.94

slave安装：

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

end






