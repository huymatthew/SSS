from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Subject, Schedule
import json


def schedule_list(request):
    """View để hiển thị danh sách các schedule"""
    schedules = Schedule.objects.all().order_by('-created_at')
    return render(request, 'schedule_editor/schedule_list.html', {'schedules': schedules})


def schedule_editor(request, schedule_id):
    """View chính cho trang schedule editor"""
    subjects = Subject.objects.all().order_by('name')
    return render(request, 'schedule_editor/editor.html', {'subjects': subjects, 'schedule_id': schedule_id})

