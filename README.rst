============
crondeamon
============
***************
1.介绍
***************
crondeamon是用来管理计划任务及后台任务的项目， 其功能相当于supervisor+crontab。   crondeamon集群有三个角色：
1.slave  slave主要是用来控制进程的启动和销毁，
2.master master主要是集中控制所有的slave节点。
3.ui     ui主要是提供web界面