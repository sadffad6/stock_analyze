from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# 正确的导入方式
from rest_framework.authtoken.models import Token
class RegisterView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user

