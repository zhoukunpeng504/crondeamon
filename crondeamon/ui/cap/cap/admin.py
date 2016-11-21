__author__ = 'zhou'
from django.contrib import  admin
from models import Project
from cron.models import App,CronServe
admin.site.register([CronServe,Project,App])