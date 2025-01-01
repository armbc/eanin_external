from django.urls import path
from app01 import views

urlpatterns = [
    # ----------- 首页 -----------
    path('', views.index, name='index'),
    # path('test/', views.TestAPIView.as_view(), name='test'),

]
