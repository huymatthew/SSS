from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Subject, Schedule, ScheduleItem
import json

"""================ SCHEDULES API ================"""
@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def add_schedule(request):
    """API để tạo lịch học mới"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule = Schedule.objects.create(
                name=data.get('name', 'New Schedule'),
                created_by=request.user
            )
            return JsonResponse({
                'success': True,
                'schedule': {
                    'id': schedule.id,
                    'name': schedule.name,
                    'created_at': schedule.created_at
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ'})

def remove_schedule(request, schedule_id):
    """API để xóa lịch học"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'DELETE':
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.delete()
            return JsonResponse({'success': True})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lịch học không tồn tại'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ'})
                                                                                    
"""================ SUBJECTS API ================"""
@csrf_exempt
@require_http_methods(["GET", "POST"])
def subjects_api(request):
    """API để quản lý danh sách môn học"""
    if request.method == 'GET':
        subjects = ScheduleItem.objects.filter(schedule__created_by=request.user, schedule__id=request.GET['schedule_id']).values('id', 'name', 'subject__code', 'subject__credits', 'color')
        return JsonResponse({'subjects': list(subjects)})

@csrf_exempt
@require_http_methods(["GET"])
def search_subjects(request):
    """API để search subjects với suggestions"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    
    if not query:
        return JsonResponse({'subjects': []})
    
    # Search trong name và code
    subjects = Subject.objects.filter(
        models.Q(name__istartswith=query) |
        models.Q(code__istartswith=query)
    ).values(
        'id', 'name', 'code', 'credits', 'professor',
        'day', 'startperiod', 'endperiod', 'room',
        'color', 'semester', 'weeks'
    )[:limit]
    
    return JsonResponse({'subjects': list(subjects)})

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def schedule_item_api(request):
    """API để thêm hoặc xóa môn học khỏi lịch học"""
    try:
        data = json.loads(request.body)
        print(data)
        schedule = Schedule.objects.get(id=data.get('schedule_id'))
        print(schedule)
        subject = Subject.objects.get(id=data.get('item_id'))
        print(subject)
        
    except (Schedule.DoesNotExist, Subject.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Mục lịch học không tồn tại'})
    
    if request.method == 'PUT':
        try:
            item = ScheduleItem()
            item.schedule = schedule
            item.subject = subject
            item.name = subject.name
            item.day = subject.day
            item.startperiod = subject.startperiod
            item.endperiod = subject.endperiod
            item.room = subject.room
            item.color = subject.color
            item.save()
            
            return JsonResponse({
                'success': True,
                'item': {
                    'id': str(item.id),
                    'name': item.name,
                    'day': str(item.day),
                    'startperiod': str(item.startperiod),
                    'endperiod': str(item.endperiod),
                    'room': item.room,
                    'color': item.color
                }
            })
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})    
    elif request.method == 'DELETE':
        try:
            item = ScheduleItem.objects.get(schedule=schedule, subject=subject)
            item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    