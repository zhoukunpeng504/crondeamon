#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/11.
# ---------------------------------

from setuptools import  setup,find_packages
setup(
    name="crondeamon",
    packages=list(set(list(find_packages())+["twisted.plugins"])),
    version='0.1.1',
    install_requires=["setuptools", "MySQL-python","twisted","txscheduling","psutil","django==1.4.16"],
    include_package_data=True
)