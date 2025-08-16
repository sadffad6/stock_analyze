from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db import models
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from user.models import FirstLoginRecord
from home.models import UserVector
class RegisterView(APIView):
    permission_classes = [AllowAny]  # 注册界面允许公开访问

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"status": 400, "message": "用户名和密码不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"status": 400, "message": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(password)  # 使用加密的密码
            user.save()
            # 创建对应的首次登录记录对象，初始化为首次登录状态
            FirstLoginRecord.objects.create(user=user)

            # 新增：为新注册用户创建对应的UserVector记录，使用设置好默认值的方式创建
            user_vector = UserVector(user=user)
            user_vector.save()

            return Response({"status": 200, "message": "注册成功"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": 400, "message": f"注册失败：{e}"}, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    permission_classes = [AllowAny]  # 登录界面允许公开访问

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"status": 400, "message": "用户名和密码不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            try:
                # 获取该用户对应的首次登录记录对象
                first_login_record = FirstLoginRecord.objects.get(user=user)
                is_first_login = first_login_record.is_first_login
                if is_first_login:
                    print(f"用户 {user.id} 首次登录，更新首次登录状态为 false")
                    first_login_record.is_first_login = False
                    first_login_record.save()
            except FirstLoginRecord.DoesNotExist:
                # 若不存在记录，视为首次登录（这种情况可能是数据异常等情况导致，可按需进一步处理）
                is_first_login = True

            return Response({
                "status": 200,
                "message": "登录成功",
                "data": {
                    "username": user.username,
                    "token": token.key
                },
                "isFirstLogin": is_first_login
            }, status=status.HTTP_200_OK)
        else:
            return Response({"status": 400, "message": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST)