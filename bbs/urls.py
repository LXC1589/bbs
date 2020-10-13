"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from luntan import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(r'', views.login),  # 默认登录界面
    path(r'index/', views.index),  # 主页
    path(r'reg/', views.reg),  # 注册
    path(r'login/', views.login),  # 登录
    path(r'reset_psw/', views.reset_psw),  #找回密码
    path(r'active/', views.active),#提示注册成功
    path(r'personal_info/', views.personal_info),  # 个人信息展示页
    path(r'logout/', views.logout),  # 退出登录
]
