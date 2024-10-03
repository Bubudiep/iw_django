import json
import sys
import os
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
        # allowed_domains = ['ipays.vn', 'example.com', 'anotherdomain.com']  # Thêm các domain hợp lệ vào đây
        # if referer is None or not any(referer.startswith(f'http://{domain}') or referer.startswith(f'https://{domain}') for domain in allowed_domains):
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
            qs_app = Application.objects.first()
            expires_in_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 3600)
            expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
            access_token_str = generate_short_token(length=32)  # Token ngắn
            refresh_token_str = generate_refresh_token(length=32)  # Refresh token ngắn
            try:
                token = AccessToken.objects.create(
                    user=user,
                    application=qs_app,
                    token=access_token_str,
                    expires=expires_at
                )
                # Trả về token
                return JsonResponse({
                    'access_token': access_token_str,
                    'expires_in': expires_in_seconds,
                    'token_type': 'Bearer',
                    'scope': 'read write',
                    'refresh_token': refresh_token_str,
                })
            except Exception as e:
                return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        user = self.request.user
        if user.is_superuser:
            return Profile.objects.all()  # Admin có thể xem tất cả ảnh
        return Profile.objects.filter(user=user)

class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AlbumFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Album.objects.all()  # Admin có thể xem tất cả ảnh
        return Album.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
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
    
class PhotosViewSet(viewsets.ModelViewSet):
    serializer_class = PhotosSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PhotosFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Photos.objects.all()  # Admin có thể xem tất cả ảnh
        return Photos.objects.filter(user=self.request.user,is_active=True)

    def create(self, request, *args, **kwargs):
        # Set the user to the authenticated user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user field
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def list(self, request, *args, **kwargs):
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
    
class TuchamcongViewSet(viewsets.ModelViewSet):
    serializer_class = TuchamcongSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination
    filterset_class = TuchamcongFilter
    
    def create(self, request, *args, **kwargs):
        # Set the user to the authenticated user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user field
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tuchamcong.objects.all()
        return Tuchamcong.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TutinhluongViewSet(viewsets.ModelViewSet):
    serializer_class = TutinhluongSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TutinhluongFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tutinhluong.objects.all()
        return Tutinhluong.objects.filter(tuchamcong__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TutinhChuyencanViewSet(viewsets.ModelViewSet):
    serializer_class = TutinhChuyencanSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return TutinhChuyencan.objects.all()
        return TutinhChuyencan.objects.filter(tuchamcong__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TuchamcongtayViewSet(viewsets.ModelViewSet):
    serializer_class = TuchamcongtaySerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination
    filterset_class = TuchamcongtayFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tuchamcongtay.objects.all()
        return Tuchamcongtay.objects.filter(tuchamcong__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class KieungayViewSet(viewsets.ModelViewSet):
    serializer_class = KieungaySerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = KieungayFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Kieungay.objects.all()
        return Kieungay.objects.filter(tuchamcong__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class KieucaViewSet(viewsets.ModelViewSet):
    serializer_class = KieucaSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = KieucaFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Kieuca.objects.all()
        return Kieuca.objects.filter(tuchamcong__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HesoViewSet(viewsets.ModelViewSet):
    serializer_class = HesoSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HesoFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Heso.objects.all()
        return Heso.objects.filter(tuchamcong__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CongtyViewSet(viewsets.ModelViewSet):
    serializer_class = CongtySerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CongtyFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Congty.objects.all()
        return Congty.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        # Set the user to the authenticated user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user field
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)