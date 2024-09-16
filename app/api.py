import json
import sys
import requests
import secrets
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
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from django.conf import settings
from oauth2_provider.oauth2_backends import OAuthLibCore
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import string
from .filters import *
from django_filters.rest_framework import DjangoFilterBackend
  
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 100
    
def generate_response_json(result:str, message:str, data:dict={}):
    """_summary_

    Args:
        result (str): PASS / FAIL
        message (str): Description
        data (dict): dict data

    Raises:
        Exception: _description_

    Returns:
        dict: Response Packaged
    """
    # logger.debug(f"Result: {result}, Message: {message}, Data: {data}")
    return {"result": result, "message": message, "data": data}

class CustomTokenView(TokenView):
    permission_classes = [permissions.AllowAny]


def generate_short_token(length=32):
    """Tạo token ngắn với độ dài cụ thể, chỉ chứa chữ cái và số."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_short_token(length=32):
    """Tạo token ngắn với độ dài cụ thể, chỉ chứa chữ cái và số."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_refresh_token(length=32):
    """Tạo refresh token ngắn với độ dài cụ thể."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

class ZaloLoginAPIView(APIView):
    def post(self, request):
        # Check the referer
        # referer = request.META.get('HTTP_REFERER')
        # allowed_domain = 'ipays.vn'
        # if referer is None or not referer.startswith(f'http://{allowed_domain}') and not referer.startswith(f'https://{allowed_domain}'):
        #     return Response({'detail': 'Invalid referer'}, status=status.HTTP_403_FORBIDDEN)

        zalo_id = request.data.get('zalo_id')

        if not zalo_id:
            return Response({'detail': 'Zalo ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Xác thực người dùng qua zalo_id
        profile = get_object_or_404(Profile, zalo_id=zalo_id)
        user = profile.user
        qs_app = Application.objects.first()
        expires_in_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 3600)
        
        # Tính toán thời gian hết hạn
        expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)

        # Tạo token và refresh token
        access_token_str = generate_short_token(length=32)  # Token ngắn
        refresh_token_str = generate_refresh_token(length=32)  # Refresh token ngắn

        # Tạo token mới cho người dùng
        try:
            token = AccessToken.objects.create(
                user=user,
                application=qs_app,
                token=access_token_str,
                expires=expires_at
            )
        except Exception as e:
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Trả về token
        return JsonResponse({
            'access_token': access_token_str,
            'expires_in': expires_in_seconds,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': refresh_token_str,
        })
        
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            # Chỉ lấy thông tin của chính người dùng
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            serializer = self.get_serializer(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Chỉ trả về Profile của người dùng hiện tại
        return Profile.objects.filter(user=self.request.user)

class PhotosViewSet(viewsets.ModelViewSet):
    serializer_class = PhotosSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PhotosFilter

    def get_queryset(self):
        return Photos.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override the default `list` method to apply custom filtering and pagination.
        """
        queryset = self.get_queryset()
        filterset = self.filterset_class(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        else:
            return Response({'errors': filterset.errors}, status=400)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
# WorkSheet ViewSet
class WorkSheetViewSet(viewsets.ModelViewSet):
    serializer_class = WorkSheetSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Chỉ trả về WorkSheet của người dùng hiện tại
        return WorkSheet.objects.filter(user=self.request.user)

# WorkSalary ViewSet
class WorkSalaryViewSet(viewsets.ModelViewSet):
    serializer_class = WorkSalarySerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Chỉ trả về WorkSalary của WorkSheet thuộc về người dùng hiện tại
        return WorkSalary.objects.filter(worksheet__user=self.request.user)

# WorkRecord ViewSet
class WorkRecordViewSet(viewsets.ModelViewSet):
    serializer_class = WorkRecordSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Chỉ trả về WorkRecord của WorkSheet thuộc về người dùng hiện tại
        return WorkRecord.objects.filter(worksheet__user=self.request.user)