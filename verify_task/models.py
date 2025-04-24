# models.py
# from django.db import models
# from django.db.models.signals import post_save
# from appsec_task.models import AppSecTask

# from django.db import models


# class VerifyTask(models.Model):
#     STATUS_CHOICES = [
#         ('Not Start', 'Not Start'),
#         ('In Progress', 'In Progress'),
#         ('Done', 'Done'),
#         ('Cancel', "Cancel")
#     ]
#     # task description
#     appsec_task = models.ForeignKey('appsec_task.AppSecTask', related_name="verify_tasks",on_delete=models.SET_NULL, null=True, blank=True)
#     # appsec_task = models.ForeignKey(AppSecTask, on_delete=models.CASCADE, related_name='verify_tasks', null=True, blank=True)
#     name = models.CharField(max_length=255)
#     description = models.TextField(null=True, blank=True)
#     #plan
#     PIC_ISM = models.CharField(max_length=50, null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Start')
#     start_date = models.DateField(null=True, blank=True)
#     end_date = models.DateField(null=True, blank=True)
#     is_active = models.BooleanField(default=True)
    
    
#     def __str__(self):
#         return self.name


from django.db import models
from django.core.exceptions import ValidationError
from appsec_task.models import AppSecTask
# Create your models here.
from djongo import models

class VerifyTask(models.Model):
    STATUS_CHOICES = [
        ('Not Start', 'Not Start'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Interrupt', 'Interrupt'),
        ('Cancel', "Cancel")
    ]
    
    appsec_task = models.ForeignKey('appsec_task.AppSecTask', related_name="verify_tasks",on_delete=models.SET_NULL, null=True, blank=True)
    # task description
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # plan
    PIC_ISM = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Start')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    
    def clean(self):
        """Kiểm tra điều kiện ngày tháng hợp lệ."""
        errors = {}

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors["end_date"] = "End date must be greater than or equal to start date."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()  # Quan trọng! Gọi full_clean() để kích hoạt validation
        super().save(*args, **kwargs)
        # if self.appsec_task:
        #     from appsec_task.models import sync_status  # hoặc đúng đường dẫn module
        #     sync_status(self.appsec_task.id)


    def __str__(self):
        return self.name



