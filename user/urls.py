from django.contrib import admin
from django.urls import path
from user.views import RegisterView,LoginView

urlpatterns = [

    path("register", RegisterView.as_view(), name="register"),  # 使用类视图时添加 .as_view()
    path('login', LoginView.as_view(), name='login'),
]
