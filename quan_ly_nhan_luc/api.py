import json
import sys
import os
import requests
import secrets
import socketio
from rest_framework import viewsets
from rest_framework import permissions
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView
from oauth2_provider.views import TokenView
from oauth2_provider.models import AccessToken, Application
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.models import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from .filters import *
from app.socket import send_socket
from oauth2_provider.settings import oauth2_settings
from django.contrib.auth import authenticate
from oauthlib.common import generate_token
from datetime import timedelta
from django.utils.timezone import now

class LoginOAuth2APIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print("Đang đăng nhập")
        username = request.data.get('username')
        password = request.data.get('password')
        key = request.data.get('key')
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'Error': 'Tài khoản hoặc mật khẩu không chính xác'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            qs_company = company_staff.objects.get(user=user, company__key=key,)
            if qs_company.isBan:
                return Response({'Error': 'Tài khoản của bạn đã bị cấm!'}, status=status.HTTP_403_FORBIDDEN)
            if qs_company.isActive==False:
                return Response({'Error': 'Tài khoản của bạn đã bị khóa!'}, status=status.HTTP_403_FORBIDDEN)
        except company_staff.DoesNotExist:
            return Response({'Error': 'Bạn không nằm trong công ty này!'}, status=status.HTTP_403_FORBIDDEN)
        application = Application.objects.filter(client_id='G061oKzH80Y7k7Q8mcqlrnSpFH2OhSl2N6Ye0RLS').first()
        if not application:
            return Response({'Error': 'OAuth2 Application not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token = generate_token()
        access_token = AccessToken.objects.create(
            user=user,
            token=token,
            application=application,
            expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
            scope='read write'
        )
        refresh_token_instance = RefreshToken.objects.create(
            user=user,
            token=generate_token(),
            access_token=access_token,
            application=application
        )
        access_token.refresh_token = refresh_token_instance
        access_token.save()
        return Response({
            'access_token': token,
            'refresh_token': refresh_token_instance.token,
            'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            'token_type': 'Bearer',
            'scope': access_token.scope,
            'company': companySerializer(qs_company.company).data,
            'user': company_staffSerializer(qs_company).data
        }, status=status.HTTP_200_OK)
       
class GetUserAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key=request.query_params.get('key')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_company=company_staff.objects.get(user=user,company__key=key)
                return Response({
                    'company': companySerializer(qs_company.company).data,
                    'user': company_staffSerializer(qs_company).data
                }, status=status.HTTP_200_OK)
            except company_staff.DoesNotExist:
                return Response({'Error': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
        
class GetCompanyAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key=request.query_params.get('key')
        print(f"{key}")
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_company=company_staff.objects.get(user=user,company__key=key)
                return Response(companySerializer(qs_company.company).data, status=status.HTTP_200_OK)
            except company_staff.DoesNotExist:
                return Response({'Error': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)