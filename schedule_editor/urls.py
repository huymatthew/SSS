from django.urls import path
from . import views
from . import api

app_name = 'schedule_editor'

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('editor/<int:schedule_id>/', views.schedule_editor, name='editor'),
    path('api/subjects/', api.subjects_api, name='subjects_api'),
    path('api/search-subjects/', api.search_subjects, name='search_subjects'),
    path('api/schedule_item_api/', api.schedule_item_api, name='schedule_item_api'),
    
    path('api/add-schedule/', api.add_schedule, name='add_schedule'),
    path('api/remove-schedule/<int:schedule_id>/', api.remove_schedule, name='remove_schedule'),
]