# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by  zhoukunpeng  on 2016/11/11.
# ---------------------------------

from setuptools import setup, find_packages

setup(
    name="crondeamon",
    packages=list(set(list(find_packages()) + ["twisted.plugins"])),
    version='0.1.4',
    install_requires=["setuptools", "MySQL-python", "twisted==20.3.0", "txscheduling", "psutil", "django==1.4.22"],
    include_package_data=True
)
