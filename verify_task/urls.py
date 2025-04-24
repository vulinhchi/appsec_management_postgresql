# from django.conf.urls import url, include
from django.urls import path
# from .views import create_pentest_task, list_pentest_tasks
from . import views

app_name = 'verify_task'

urlpatterns = [
    path('create/<int:appsec_task_id>/', views.create_verify_task, name='create_verify_task'),
    path('list/', views.list_verify_tasks, name='list_verify_tasks'),
    path('edit/<int:verify_task_id>/', views.edit_verify_task, name='edit_verify_task'),
    path('delete/<int:verify_task_id>/', views.delete_verify_task, name='delete_verify_task'),
    path('view/<int:verify_task_id>/', views.view_verify_task, name='view_verify_task'),
    
]