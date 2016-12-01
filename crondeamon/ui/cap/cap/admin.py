__author__ = 'zhou'
from django.contrib import  admin
from cron.models import CronServe
admin.site.register([CronServe])