from django.contrib import admin
from django.urls import path
from user.views import RegisterView,LoginView

urlpatterns = [

    # path("/agents/compare", RegisterView.as_view(), name="register"),  # 使用类视图时添加 .as_view()
]
