from django.urls import path
from app01 import views

urlpatterns = [
    # ----------- 首页 -----------
    path('', views.index, name='index'),
    # ----------- 蛋糕分类展示 -----------
    path('cake/', views.cake_list, name='cake_list'),   # 蛋糕分类展示

    # ----------- 测试专用 -----------
    path('test/', views.test_api, name='test_api'),

]
