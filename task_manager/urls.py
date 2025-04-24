"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from martor import urls as martor_urls  # 🔥 Import đúng cách
from pentest_task.views import martor_upload_image  # Import đúng app
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# from pentest_task.views import MarkdownUploadView

# from .views import create_task

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pentest/', include('pentest_task.urls', namespace='pentest_task')),
    path('verify/', include('verify_task.urls', namespace='verify_task')),
    path('', include('appsec_task.urls', namespace='appsec_task')), 
    path('i18n/', include('django.conf.urls.i18n')),
    # path("martor/uploader/", martor_upload_image, name="martor_upload_image"), 
    path('martor/', include('martor.urls')),
    path("api/uploader/", martor_upload_image, name="martor_upload_image"), 
    path('accounts/', include('accounts.urls')),
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Gán handler404 để Django sử dụng trang 404 tùy chỉnh
handler404 = 'pentest_task.views.custom_404_view'

