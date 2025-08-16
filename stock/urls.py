from django.contrib import admin
from django.urls import path
from user.views import RegisterView,LoginView
from stock.views import MarketShowView
urlpatterns = [

    path("market", MarketShowView.as_view()),  # 使用类视图时添加 .as_view()
]
