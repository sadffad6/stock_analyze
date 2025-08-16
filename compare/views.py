from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# 正确的导入方式
from rest_framework.authtoken.models import Token
class RegisterView(APIView):
    permission_classes = [AllowAny]


    def get(self, request):
        return Response({"status": 200, "message": "收到"}, status=status.HTTP_201_CREATED)


    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # 基本验证
        if not username or not password:
            return Response(
                {"message": "用户名和密码不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "用户名已存在"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建用户
        try:
            user = User(username=username)
            user.set_password(password)  # 密码加密存储
            user.save()

            return Response(
                {"message": "注册成功"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"message": f"注册失败：{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # 基本验证
        if not username or not password:
            return Response(
                {"message": "用户名和密码不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证用户
        user = authenticate(username=username, password=password)
        if user:
            # 获取或创建Token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "登录成功",
                "data": {
                    "username": user.username,
                    "token": token.key
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "用户名或密码错误"},
                status=status.HTTP_400_BAD_REQUEST
            )