from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    """Mô hình dữ liệu cho môn học"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=3)
    professor = models.CharField(max_length=100, blank=True)
    startperiod = models.IntegerField(null=True, blank=True)  # Thời gian bắt đầu tiết (1-12)
    endperiod = models.IntegerField(null=True, blank=True)    # Thời gian kết thúc tiết (1-12)
    day = models.IntegerField(choices=[
        (1, 'Thứ Hai'),
        (2, 'Thứ Ba'),
        (3, 'Thứ Tư'),
        (4, 'Thứ Năm'),
        (5, 'Thứ Sáu'),
        (6, 'Thứ Bảy'),
        (7, 'Chủ Nhật'),
    ], null=True, blank=True)
    room = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#3498db')  # Màu mặc định
    semester = models.CharField(max_length=20, blank=True) # 1-2025/2-2025/h-2025
    weeks = models.CharField(max_length=100, blank=True) # 1-16/1-8,10-16
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class Schedule(models.Model):
    """Mô hình dữ liệu cho lịch học"""
    name = models.CharField(max_length=200)
    semester = models.CharField(max_length=20, blank=True) # 1-2025/2-2025/h-2025
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.name
    
class ScheduleItem(models.Model):
    """Mô hình dữ liệu cho mục trong lịch học"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    day = models.IntegerField()
    startperiod = models.IntegerField()
    endperiod = models.IntegerField()
    room = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#3498db')
    def __str__(self):
        return f"{self.schedule.name} - {self.subject.code} on {self.get_day_display()}"