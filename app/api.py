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
from rest_framework.exceptions import AuthenticationFailed
  
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

class ThemnguoivaoAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            nhaTro=data.get("tro",None)
            if nhaTro is None:
                return Response({'Error': "Chưa chọn nhà trọ"}, status=status.HTTP_400_BAD_REQUEST)
            soPhong=data.get("phong",None)
            if soPhong is None:
                return Response({'Error': "Chưa nhập số phòng"}, status=status.HTTP_400_BAD_REQUEST)
            tenTang=data.get("tang",None)
            if tenTang is None:
                return Response({'Error': "Chưa nhập tên tầng"}, status=status.HTTP_400_BAD_REQUEST)
            qs_phong=Phong.objects.get(
                id=soPhong, 
                tang__id=tenTang, 
                tang__nhaTro__id=nhaTro, 
                tang__nhaTro__user=request.user
            )
            nguoitro, _ = Nguoitro.objects.get_or_create(
                cccd=data.get("cccd", None),
                defaults={
                    'hoTen': data.get("hoTen", None),
                    'sdt': data.get("sdt", None)
                }
            )
            lichsu_otro=LichsuNguoitro.objects.create(nguoiTro=nguoitro,
                                            phong=qs_phong,
                                            ngayBatdauO=data.get("ngayBatDau", None))
            qs_nhatro=Nhatro.objects.filter(user=request.user)
            return Response(NhatroDetailsSerializer(qs_nhatro,many=True).data, status=status.HTTP_201_CREATED)
        except Tang.DoesNotExist:
            return Response({'Error': "Không tìm thấy tầng"}, status=status.HTTP_404_NOT_FOUND)
        except Phong.DoesNotExist:
            return Response({'Error': "Không tìm thấy phòng"}, status=status.HTTP_404_NOT_FOUND)
        except Nhatro.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class NhaTroCreateView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            nhaTro=data.get("tenTro",None)
            if nhaTro is None:
                return Response({'Error': "Chưa nhập tên trọ"}, status=status.HTTP_400_BAD_REQUEST)
            list_tang=data.get("tangs",None)
            if list_tang is None:
                return Response({'Error': "Chưa có tầng"}, status=status.HTTP_400_BAD_REQUEST)
            qs_nhatro=Nhatro.objects.create(tenTro=nhaTro,user=request.user)
            for tang in list_tang:
                create_tang=Tang.objects.create(nhaTro=qs_nhatro,tenTang=f"Tầng {tang.get('soTang',None)}")
                for phong in range(int(tang.get('phongBatDau',0)),int(tang.get('phongKetThuc',0))+1):
                    create_phong=Phong.objects.create(tang=create_tang,soPhong=f"Phòng {phong}")

            qs_nhatro=Nhatro.objects.filter(user=request.user)
            return Response(NhatroDetailsSerializer(qs_nhatro,many=True).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
    
class ThemtangAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            nhaTro=data.get("nhaTro",None)
            if nhaTro is None:
                return Response({'Error': "Chưa chọn nhà trọ"}, status=status.HTTP_400_BAD_REQUEST)
            soPhong=data.get("soPhong",None)
            if soPhong is None:
                return Response({'Error': "Chưa nhập số phòng"}, status=status.HTTP_400_BAD_REQUEST)
            tenTang=data.get("soTang",None)
            if tenTang is None:
                return Response({'Error': "Chưa nhập tên tầng"}, status=status.HTTP_400_BAD_REQUEST)
            taoPhong=data.get("taoPhong",None)
            if taoPhong is None:
                return Response({'Error': "Bạn đang sử dụng phiên bản khác"}, status=status.HTTP_400_BAD_REQUEST)
            qs_nhatro=Nhatro.objects.get(id=nhaTro,user=request.user)
            qs_old_tang=Tang.objects.filter(tenTang=tenTang,nhaTro=qs_nhatro)
            if len(qs_old_tang)>0:
                return Response({'Error': f"{tenTang} đã được thêm vào trước đó!"}, status=status.HTTP_404_NOT_FOUND)
            qs_tang=Tang.objects.create(tenTang=tenTang,nhaTro=qs_nhatro)
            if taoPhong:
                for tao in range(0,int(soPhong)):
                    Phong.objects.create(tang=qs_tang,soPhong=f"Phòng {tao+1}")
            # Trả về phản hồi thành công
            return Response(NhatroDetailsSerializer(qs_nhatro,many=False).data, status=status.HTTP_201_CREATED)
        except Nhatro.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class ZaloLoginAPIView(APIView):
    def post(self, request):
        zalo_id = request.data.get('zalo_id')

        if not zalo_id:
            return Response({'detail': 'Zalo ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Xác thực người dùng qua zalo_id
        profile = get_object_or_404(Profile, zalo_id=zalo_id)
        user = profile.user
        qs_app = Application.objects.first()
        expires_in_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 360000)
        
        # Lấy thời gian hiện tại
        now = timezone.now()

        # Kiểm tra xem có token nào còn hạn không
        existing_tokens = AccessToken.objects.filter(user=user, application=qs_app)

        # Xóa token nào đã hết hạn
        for token in existing_tokens:
            if token.expires < now:
                token.delete()

        # Nếu còn token hợp lệ, trả về token đó
        valid_token = existing_tokens.filter(expires__gt=now).first()
        if valid_token:
            return JsonResponse({
                'access_token': valid_token.token,
                'expires_in': int((valid_token.expires - now).total_seconds()),
                'token_type': 'Bearer',
                'scope': valid_token.scope,
                'refresh_token': 'existing_refresh_token',  # Add your logic to handle refresh tokens
            })

        # Nếu không có token hợp lệ, tạo token mới
        expires_at = now + timedelta(seconds=expires_in_seconds)

        # Tạo token mới cho người dùng
        access_token_str = generate_short_token(length=32)  # Token ngắn
        refresh_token_str = generate_refresh_token(length=32)  # Refresh token ngắn

        try:
            token = AccessToken.objects.create(
                user=user,
                application=qs_app,
                token=access_token_str,
                expires=expires_at
            )
        except Exception as e:
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Trả về token mới
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
    
class DanhsachNhatroViewSet(viewsets.ModelViewSet):
    serializer_class = NhatroDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NhatroFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Nhatro.objects.all()
        return Nhatro.objects.filter(user=user)

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
    
class NhatroViewSet(viewsets.ModelViewSet):
    serializer_class = NhatroSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NhatroFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Nhatro.objects.all()
        return Nhatro.objects.filter(user=user)

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
    
class DanhsachCongtyViewSet(viewsets.ModelViewSet):
    serializer_class = DanhsachCongtySerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DanhsachCongtyFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DanhsachCongty.objects.all()
        return DanhsachCongty.objects.filter(user=user)

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
    
class DanhsachNhanvienViewSet(viewsets.ModelViewSet):
    serializer_class = DanhsachNhanvienSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DanhsachNhanvienFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DanhsachNhanvien.objects.all()
        #
        qs_profile=Profile.objects.get(user=user)
        qs_admin=DanhsachAdmin.objects.get(zalo_id=qs_profile.zalo_id)
        return DanhsachNhanvien.objects.filter(congty=qs_admin.congty)

    
    def create(self, request, *args, **kwargs):
        # Set the user to the authenticated user
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        if user.is_superuser:
            if serializer.is_valid():
                serializer.save()
        else:
            if serializer.is_valid():
                qs_profile=Profile.objects.get(user=user)
                qs_admin=DanhsachAdmin.objects.filter(zalo_id=qs_profile.zalo_id,congty=request.data.get("congty", None))
                if len(qs_admin)>0:
                    serializer.save()  # Set the user field
                    return Response(serializer.data, status=201)
                else:
                    return Response(data={"Error":"Bạn không phải nhân viên của công ty này!"}, status=400)
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
    
class DanhsachAdminViewSet(viewsets.ModelViewSet):
    serializer_class = DanhsachAdminSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DanhsachAdminFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DanhsachAdmin.objects.all()
        #
        qs_profile=Profile.objects.get(user=user)
        return DanhsachAdmin.objects.filter(zalo_id=qs_profile.zalo_id)

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
    
class DanhsachnhanvienDilamViewSet(viewsets.ModelViewSet):
    serializer_class = DanhsachnhanvienDilamDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DanhsachnhanvienDilamFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DanhsachnhanvienDilam.objects.all()
        #
        qs_profile=Profile.objects.get(user=user)
        qs_admin=DanhsachAdmin.objects.filter(zalo_id=qs_profile.zalo_id).values_list("congty__id",flat=True)
        qs_nhanvien=DanhsachNhanvien.objects.filter(congty__in=qs_admin).values_list("id",flat=True)
        return DanhsachnhanvienDilam.objects.filter(manhanvien__in=qs_nhanvien)

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
        
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class DilamAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET' or self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        data = request.query_params
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        token = None
        # Extract the token from the Authorization header
        if auth_header is not None:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        # Handle case where token is not provided
        if token is None:
            return Response({'detail': 'Authorization token is missing.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Validate the token
            vaolam=False
            if data.get("chamcongdi",None)=="true":
                vaolam=True
            qs_token = AccessToken.objects.get(token=token)
            qs_profile=Profile.objects.get(user=qs_token.user)
            qs_admin=DanhsachAdmin.objects.get(zalo_id=qs_profile.zalo_id,congty__congty=data.get("congty"))
            qs_nv=DanhsachNhanvien.objects.get(manhanvien=data.get("manhanvien"),congty=qs_admin.congty)
            dilam=DanhsachnhanvienDilam.objects.create(manhanvien=qs_nv,chamcongdi=vaolam,ngaydilam=data.get("ngaylam",None))
            print(f"{qs_nv}")
            return Response(DanhsachnhanvienDilamDetailsSerializer(dilam,many=False).data)
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Proceed with processing if the token is valid
        return Response(data={'params': data, 'token': token})
    
    def post(self, request):
        res_data = dict()
        res_status = status.HTTP_200_OK
        try:
            client_data = request.data
            rmItems=client_data.get("rm_item",None)
            send_mail=client_data.get("send_mail",None)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")

        return Response(data=res_data, status=res_status)   