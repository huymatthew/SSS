from django.contrib import admin
from .models import Subject, Schedule, ScheduleItem
# Register your models here.

admin.site.register(Subject)
admin.site.register(Schedule)
admin.site.register(ScheduleItem)
