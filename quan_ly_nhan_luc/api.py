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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import check_password
from rest_framework.filters import OrderingFilter

def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 9999
class StaffCreateMini(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        key=request.data.get("key",None)
        func=request.data.get("func",None)
        data=request.data.get("data",None)
        user = self.request.user
        if user.is_authenticated:
            if key is None:
                return Response({"Error":"Công ty không hợp lệ!"}, status=status.HTTP_400_BAD_REQUEST)
            if func is None:
                return Response({"Error":"Chức năng không hợp lệ!"}, status=status.HTTP_400_BAD_REQUEST)
            if data is None:
                return Response({"Error":"Nội dung không hợp lệ!"}, status=status.HTTP_400_BAD_REQUEST)
            if func=="possition":
                pos_name=data.get("positionName")
                pos_des=data.get("jobDescription")
                qs_company=company_staff.objects.get(user__user=user,company__key=key,isAdmin=True)
                new_pos=company_possition.objects.create(company=qs_company.company,
                                                         name=pos_name,
                                                         description=pos_des,
                                                         isActive=True)
                return  Response(company_possitionSerializer(new_pos).data, status=status.HTTP_201_CREATED)
            if func=="department":
                pos_name=data.get("departmentName")
                pos_des=data.get("description")
                qs_company=company_staff.objects.get(user__user=user,company__key=key,isAdmin=True)
                new_dpm=company_department.objects.create(company=qs_company.company,
                                                         name=pos_name,
                                                         description=pos_des,
                                                         isActive=True)
                return  Response(company_departmentSerializer(new_dpm).data, status=status.HTTP_201_CREATED)
            return Response({"Error":"Lỗi khởi tạo!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error":"Bạn không có quyền!"}, status=status.HTTP_400_BAD_REQUEST)
               
class RegisterView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            qs_staff=company_staff.objects.get(user=user)
            return Response(CompanyStaffDetailsSerializer(qs_staff).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
               
class LoginOAuth2APIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            username = request.data.get('username')
            password = request.data.get('password')
            key = request.data.get('key')
            try:
                company_instance =company.objects.get(key=key)
                user=company_account.objects.get(username=username,company=company_instance )
                if check_password(password, user.password)==False:
                    return Response({'Error': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            except company.DoesNotExist:
                return Response({'Error': 'Công ty chưa được đăng ký'}, status=status.HTTP_401_UNAUTHORIZED)
            except company_account.DoesNotExist:
                return Response({'Error': 'Tài khoản không chính xác'}, status=status.HTTP_401_UNAUTHORIZED)
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
                user=user.user,
                token=token,
                application=application,
                expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                scope='read write'
            )
            refresh_token_instance = RefreshToken.objects.create(
                user=user.user,
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
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
       
class GetUserAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key=request.query_params.get('key')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=company_staff.objects.get(user__user=user,company__key=key)
                qs_profile=None
                try:
                    qs_profile=company_staff_profile.objects.get(staff=qs_staff)
                except:
                    pass
                return Response({
                    'company': companyDetailsSerializer(qs_staff.company).data,
                    'user': company_staffSerializer(qs_staff).data,
                    'profile': company_staff_profileSerializer(qs_profile).data if qs_profile else None
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
                return Response(companyDetailsSerializer(qs_company.company).data, status=status.HTTP_200_OK)
            except company_staff.DoesNotExist:
                return Response({'Error': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)


class CompanyStaffViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyStaffDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    filterset_class = CompanyStaffFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return company_staff.objects.all()
        qs_res=company_staff.objects.filter(user__user=user,isActive=True).values_list("company__id",flat=True)
        return company_staff.objects.filter(company__id__in=qs_res)
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
