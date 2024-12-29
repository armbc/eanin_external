from django.contrib import admin
from django.urls import path
from app01 import views

urlpatterns = [
    # ----------- 首页 -----------
    path('admin/', admin.site.urls),    # 将 Django 的管理后台（admin site）映射到 URL 路径 admin/
    path('', views.index, name='index'),
    path('ai/list01/', views.ai_list01),
    path('depart/list01/', views.depart_list01),
]
