    
# from django.conf.urls import url, include
from django.urls import path
# from .views import create_pentest_task, list_pentest_tasks
from . import views

app_name = 'appsec_task'

urlpatterns = [
    path('appsec/create/', views.create_appsec_task, name='create_appsec_task'),
    path('appsec/edit/<int:task_id>/', views.edit_appsec_task, name='edit_appsec_task'),
    path('appsec/delete/<int:task_id>/', views.delete_appsec_task, name='delete_appsec_task'),
    path('appsec/view/<int:task_id>/', views.view_appsec_task, name='view_appsec_task'),
    path('appsec/list/', views.list_appsec_tasks, name='list_appsec_tasks'),

    path('appsec/import/', views.import_appsec_tasks, name='import_appsec_tasks'),
    path('appsec/export/', views.export_appsec_tasks, name='export_appsec_tasks'),

    path('appsec/list_sharecost/', views.list_sharecost, name='list_sharecost'),
    path('appsec/<int:appsec_task_id>/sharecost/add/', views.add_sharecost, name='add_sharecost'),
    path('appsec/<int:appsec_task_id>/sharecost/<int:sharecost_id>/edit/', views.edit_sharecost, name='edit_sharecost'),
    path('appsec/<int:appsec_task_id>/sharecost/<int:sharecost_id>/view/', views.view_sharecost, name='view_sharecost'),
    path('appsec/<int:appsec_task_id>//sharecost/<int:sharecost_id>/delete/', views.delete_sharecost, name='delete_sharecost'),
    path('appsec/export/sharecost/', views.export_sharecost_excel, name='export_sharecost_excel'),
    
    path('appsec/all_exceptions/', views.all_exceptions, name='all_exceptions'),
    path('appsec/<int:appsec_task_id>/exceptions/', views.exception_list, name='exception_list'),
    path('appsec/<int:appsec_task_id>/exceptions/add/', views.exception_create, name='exception_create'),
    path('appsec/<int:appsec_task_id>/exceptions/<int:pk>/edit/', views.exception_edit, name='exception_edit'),
    path('appsec/<int:appsec_task_id>/exceptions/<int:pk>/delete/', views.exception_delete, name='exception_delete'),
    path('appsec/<int:appsec_task_id>/exceptions/<int:pk>/', views.exception_detail, name='exception_detail'),

    path('', views.dashboard, name='dashboard'),
]
