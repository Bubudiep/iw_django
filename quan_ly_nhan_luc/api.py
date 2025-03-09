import json
import sys
import os
import requests
import secrets
import socketio
from django.conf import settings
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
from datetime import timedelta, datetime
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import check_password
from rest_framework.filters import OrderingFilter
from django.db.models import Q,F
from rest_framework.decorators import action
from pytz import timezone
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist

myzone = pytz.timezone('Asia/Ho_Chi_Minh')

def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}

def check_permission(user_a, permission_name):
    """
    Kiểm tra xem user_a có quyền cụ thể không.
    
    Args:
        user_a (User): Người dùng cần kiểm tra quyền.
        permission_name (str): Tên quyền cần kiểm tra.
    
    Returns:
        bool: True nếu có quyền, False nếu không.
    """
    try:
        # Lấy thông tin nhân viên từ tài khoản người dùng
        staff = company_staff.objects.get(user__user=user_a)
        # Lấy tất cả các quyền của công ty liên quan đến nhân viên (bao gồm trực tiếp, bộ phận, chức vụ)
        applicable_permissions = CompanyPermission.objects.filter(
            Q(applicable_staff=staff) |
            Q(applicable_departments=staff.department) |
            Q(applicable_positions=staff.possition),
            is_active=True,
            permission__name=permission_name,
            company=staff.company
        ).exclude(excluded_staff=staff)  # Loại trừ nếu nhân viên nằm trong danh sách bị loại trừ
        # Nếu có ít nhất một quyền phù hợp
        if applicable_permissions.exists():
            return True
        return False
    except company_staff.DoesNotExist:
        # Nhân viên không tồn tại
        return False
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 'x_forwarded_for' trả về danh sách IP cách nhau bởi dấu phẩy
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def record_user_action(function_name,
                       action_name, staff, old_data=None, 
                       new_data=None, title=None, 
                       message=None, is_hidden=False, 
                       is_sended=False, is_received=False, is_readed=False,
                       ip_action=None):
    # Kiểm tra và tạo mới function nếu chưa tồn tại
    function = company_staff_history_function.objects.get_or_create(name=function_name)[0]
    # Kiểm tra và tạo mới action nếu chưa tồn tại
    action = company_staff_history_action.objects.get_or_create(name=action_name)[0]
    # Tạo history
    history = company_staff_history.objects.create(
        ip_action=ip_action,
        staff=staff,
        function=function,
        action=action,
        old_data=old_data,
        new_data=new_data,
        title=title,
        message=message,
        isHidden=is_hidden,
        isSended=is_sended,
        isReceived=is_received,
        isReaded=is_readed,
    )
    return {
        "message": "History created successfully.",
        "data": history.id
    }
    
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 9999
class StaffCreateMini(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        key = request.headers.get('ApplicationKey')
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
       
class MyInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        key = request.headers.get('ApplicationKey')
        user=self.request.user
        if user.is_authenticated:
            try:
                qs_account=company_staff.objects.get(company__key=key,user__user=user)
                qs_profile=company_staff_profile.objects.filter(staff=qs_account)
                if len(qs_profile)==0:
                    create=company_staff_profile.objects.create(staff=qs_account)
                    return Response(company_staff_profileSerializer(create).data,status=status.HTTP_200_OK)
                else:
                    return Response({
                        "name":qs_account.name,
                        "possition":qs_account.possition.name if qs_account.possition else None,
                        "department":qs_account.department.name if qs_account.department else None,
                        **company_staff_profileSerializer(qs_profile.first()).data
                    },status=status.HTTP_200_OK)
            except company_staff.DoesNotExist:
                return Response({"detail": "Không tìm thấy công ty và tài khoản"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Bạn chưa đăng nhập"}, status=status.HTTP_400_BAD_REQUEST)
    def _save_image(self, user, image_type, image_data):
        """Lưu ảnh vào ImageSafe và trả về ID của ảnh."""
        image = image_safe(
            user=user,
            name=image_data.get('name'),  # avatar hoặc background
            data=image_data.get('data'),
            size=image_data.get('size'),
            width=image_data.get('width'),
            height=image_data.get('height'),
            fileType=image_data.get('fileType')
        )
        image.save()
        return image
    def patch(self, request, *args, **kwargs):
        key = request.headers.get('ApplicationKey')
        user = self.request.user
        if user.is_authenticated:
            try:
                qs_account = company_staff.objects.get(company__key=key, user__user=user)
                qs_profile = company_staff_profile.objects.filter(staff=qs_account).first()
                if qs_profile:
                    # Kiểm tra nếu có ảnh avatar hoặc ảnh background mới
                    if 'avatar' in request.data:
                        avatar_data = request.data['avatar']
                        create_avt=self._save_image(user, 'avatar', avatar_data)
                        qs_profile.avatar=create_avt
                    if 'background' in request.data:
                        background_data = request.data['background']
                        create_bg=self._save_image(user, 'background', background_data)
                        qs_profile.background=create_bg
                    qs_profile.save()
                    serializer = company_staff_profileSerializer(qs_profile, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response({"detail": "Hồ sơ không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)
            except company_staff.DoesNotExist:
                return Response({"detail": "Không tìm thấy công ty và tài khoản"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Bạn chưa đăng nhập"}, status=status.HTTP_400_BAD_REQUEST)
    
class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()  # Lấy từ khóa tìm kiếm
        search_type = request.query_params.get('type', '').strip()
        if not query:
            return Response({"detail": "Hãy nhập từ khóa tìm kiếm."}, status=400)
        if search_type == 'employee':
            results = company_staff_profile.objects.filter(
                Q(staff__name__icontains=query) | 
                Q(staff__user__username__icontains=query)| 
                Q(full_name__icontains=query)| 
                Q(nick_name__icontains=query)
            ).annotate(
                id=F('staff__id'),
                username=F('staff__user__username'),
                name=F('staff__name')
            ).values('id', 'name', 'username')[:8]
        elif search_type == 'department':
            results = company_department.objects.filter(
                Q(name__icontains=query)
            ).values('id', 'name')
        elif search_type == 'position':
            results = company_possition.objects.filter(
                Q(name__icontains=query)
            ).values('id', 'name')
        elif search_type == 'operator':
            results = company_operator.objects.filter(
                Q(ho_ten__icontains=query)|
                Q(ma_nhanvien__icontains=query)|
                Q(ten_goc__icontains=query)|
                Q(so_cccd__icontains=query)|
                Q(so_taikhoan__icontains=query)|
                Q(chu_taikhoan__icontains=query)|
                Q(ghichu__icontains=query)|
                Q(ghichu__icontains=query)|
                Q(nguoituyen__name__icontains=query)|
                Q(nguoituyen__company_staff_profile__full_name__icontains=query)|
                Q(nguoibaocao__name__icontains=query)|
                Q(nguoibaocao__company_staff_profile__full_name__icontains=query)
            ).values('id', 'ma_nhanvien','ho_ten')[:8]
        else:
            return Response({"detail": "Không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(results)
    
class LoginOAuth2APIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            username = request.data.get('username')
            password = request.data.get('password')
            key = request.headers.get('ApplicationKey')
            try:
                company_instance =company.objects.get(key=key)
                user=company_account.objects.get(username=username,company=company_instance )
                if check_password(password, user.password)==False:
                    return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            except company.DoesNotExist:
                return Response({'detail': 'Công ty chưa được đăng ký'}, status=status.HTTP_401_UNAUTHORIZED)
            except company_account.DoesNotExist:
                return Response({'detail': 'Tài khoản không chính xác'}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                qs_company = company_staff.objects.get(user=user, company__key=key)
                if qs_company.isBan:
                    return Response({'detail': 'Tài khoản của bạn đã bị cấm!'}, status=status.HTTP_403_FORBIDDEN)
                if qs_company.isActive==False:
                    return Response({'detail': 'Tài khoản của bạn đã bị khóa!'}, status=status.HTTP_403_FORBIDDEN)
            except company_staff.DoesNotExist:
                return Response({'detail': 'Bạn không nằm trong công ty này!'}, status=status.HTTP_403_FORBIDDEN)
            application = Application.objects.filter(client_id='G061oKzH80Y7k7Q8mcqlrnSpFH2OhSl2N6Ye0RLS').first()
            if not application:
                return Response({'detail': 'OAuth2 Application not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            print(f"{ip}")
            record_user_action(function_name="login",
                               action_name="login",
                               ip_action=ip,
                               staff=qs_company,
                               title="Đăng nhập",
                               message=f"Đăng nhập thành công tại ip {ip}",
                               is_hidden=True)
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
        key = request.headers.get('ApplicationKey')
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
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
        
class GetCompanyAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_company=company_staff.objects.get(user=user,company__key=key)
                return Response(companyDetailsSerializer(qs_company.company).data, status=status.HTTP_200_OK)
            except company_staff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
  
class GetCompanyDashboardAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_company=company_staff.objects.get(user__user=user,company__key=key).company
                qs_staff=company_staff.objects.filter(company=qs_company)
                return Response({
                    "staff":CompanyStaffSmallSerializer(qs_staff,many=True).data,
                    "departmnet":None,
                    "jobtitle":None
                }, status=status.HTTP_200_OK)
            except company_staff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = companyDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    filterset_class = CompanyFilter
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'patch']
    def _save_image(self, user, image_type, image_data):
        """Lưu ảnh vào ImageSafe và trả về ID của ảnh."""
        image = image_safe(
            user=user,
            name=image_data.get('name'),  # avatar hoặc background
            data=image_data.get('data'),
            size=image_data.get('size'),
            width=image_data.get('width'),
            height=image_data.get('height'),
            fileType=image_data.get('fileType')
        )
        image.save()
        return image
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        if user.is_superuser:
            return company.objects.all()
        return company.objects.filter(key=key)
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        key = request.headers.get('ApplicationKey')
        instance = self.get_object()
        if not user.is_superuser and not company_staff.objects.filter(company__key=key,user__user=user, isAdmin=True, isActive=True).exists():
            return Response(
                {"detail": "Bạn không có quyền thực hiện thao tác này."},
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            if 'avatar' in request.data and request.data['avatar']:
                avatar_data = request.data['avatar']
                create_avt=self._save_image(user, 'avatar', avatar_data)
                instance.avatar=create_avt
                instance.save()
            if 'wallpaper' in request.data and request.data['wallpaper']:
                wallpaper_data = request.data['wallpaper']
                create_bg=self._save_image(user, 'wallpaper', wallpaper_data)
                instance.wallpaper=create_bg
                instance.save()
        return super().partial_update(request, *args, **kwargs)
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
    
class CompanyStaffViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyStaffDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    filterset_class = CompanyStaffFilter
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'patch']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return company_staff.objects.all()
        qs_res=company_staff.objects.filter(user__user=user,isActive=True).values_list("company__id",flat=True)
        return company_staff.objects.filter(company__id__in=qs_res)
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser and not company_staff.objects.filter(user__user=user, isAdmin=True, isActive=True).exists():
            return Response(
                {"detail": "Bạn không có quyền thực hiện thao tác này."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
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
    
class CompanyAccountViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyAccountDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'patch']
    def get_queryset(self):
        user = self.request.user
        qs_res=company_staff.objects.filter(user__user=user,isActive=True).values_list("company__id",flat=True)
        return company_staff.objects.filter(company__id__in=qs_res)
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        data = request.data
        if not user.is_superuser and not company_staff.objects.filter(user__user=user, isAdmin=True, isActive=True).exists():
            return Response(
                {"detail": "Bạn không có quyền thực hiện thao tác này."},
                status=status.HTTP_403_FORBIDDEN
            )
        # Kiểm tra logic chỉ SuperAdmin mới được phép đặt tài khoản thành Admin
        if 'isAdmin' in data and data['isAdmin']:
            if not user.is_superuser and not company_staff.objects.filter(user__user=user, isSuperAdmin=True, isActive=True).exists():
                return Response(
                    {"detail": "Chỉ SuperAdmin mới có quyền đặt tài khoản này thành Admin."},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().partial_update(request, *args, **kwargs)
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
    
class CompanyDepartmentAdminViewSet(viewsets.ModelViewSet):
    serializer_class = company_departmentSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','patch','delete']
    def get_queryset(self):
        user = self.request.user
        qs_res=company_staff.objects.filter(user__user=user,isAdmin=True,isActive=True).values_list("company__id",flat=True)
        return company_department.objects.filter(company__id__in=qs_res)
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
    
class CompanyPossitionAdminViewSet(viewsets.ModelViewSet):
    serializer_class = company_possitionSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','patch','delete']
    def get_queryset(self):
        user = self.request.user
        qs_res=company_staff.objects.filter(user__user=user,isAdmin=True,isActive=True).values_list("company__id",flat=True)
        return company_possition.objects.filter(company__id__in=qs_res)
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
    
class CompanyCustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyCustomerSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','patch','delete']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company_customer.objects.filter(company=qs_res.company)
    
    def perform_create(self, serializer):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res = company_staff.objects.get(
            user__user=user,
            isActive=True,
            company__key=key
        )
        serializer.save(
            company=qs_res.company
        )
        
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            IntegrityErrorLog.objects.create(
                models_name="company_customer",
                api_name="CompanyCustomerViewSet",
                error_message=str(e),
                endpoint=request.path,
                payload=request.data
            )
            if 'UNIQUE constraint failed' in str(e):
                name=request.data.get("name")
                return Response(
                    {"detail": f"Khách hàng {name} đã tồn tại!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"detail": "Lỗi khởi tạo!"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
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
    
class CompanyVendorViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyVendorSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get','patch','delete','post']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company_vendor.objects.filter(company=qs_res.company)
    
    def perform_create(self, serializer):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res = company_staff.objects.get(
            user__user=user,
            isActive=True,
            company__key=key
        )
        serializer.save(
            company=qs_res.company
        )
        
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
    
class CompanySupplierViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySupplierSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get','patch','delete','post']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company_supplier.objects.filter(company=qs_res.company)
    
    def perform_create(self, serializer):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res = company_staff.objects.get(
            user__user=user,
            isActive=True,
            company__key=key
        )
        serializer.save(
            company=qs_res.company
        )
        
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

class CompanyOperatorViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOperatorSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get','patch','delete','post']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company_operator.objects.filter(company=qs_res.company)
    
    @action(detail=True, methods=['post'])
    def dilam(self, request, pk=None):
        startDate = request.data.get('startDate',now())
        employeeCode = request.data.get('employeeCode',None)
        company = request.data.get('company',None)
        cccd_truoc = request.data.get('cccd_truoc',None)
        cccd_sau = request.data.get('cccd_sau',None)
        if company is None:
            return Response({"detail": f"Chưa chọn công ty làm việc!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            operator = self.get_object()
            hist=operator_history.objects.filter(operator=operator).order_by('-id')
            if len(hist)!=0:
                ctyNow=hist.first()
                if datetime.strptime(startDate,"%Y-%m-%d").replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")) < ctyNow.end_date:
                    return Response({"detail": "Ngày đi làm không được nhỏ hơn ngày nghỉ ở công ty cũ!"}, status=status.HTTP_400_BAD_REQUEST)
                if ctyNow.end_date is None:
                    return Response({"detail": f"Nhân viên {operator.ho_ten} đang chưa nghỉ làm ở công ty cũ!"}, status=status.HTTP_400_BAD_REQUEST)
            qs_cty=company_customer.objects.get(id=company)
            operator.congty_danglam = qs_cty
            operator.save()
            nguoituyen = request.data.get('nguoituyen',None)
            if nguoituyen is not None:
                qs_nguoituyen=company_staff.objects.get(id=nguoituyen)
                nguoituyen=qs_nguoituyen
            else:
                nguoituyen=operator.nguoituyen
            operator_history.objects.create(ma_nhanvien=employeeCode,operator=operator,
                                            nguoituyen=nguoituyen,
                                            customer=qs_cty,start_date=startDate)
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def baoung(self, request, pk=None):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            operator = self.get_object()
            qs_com=company.objects.get(key=key)
            soTien = request.data.get('soTien',None)
            lyDo = request.data.get('lyDo',None)
            ngayUng = request.data.get('ngayUng',None)
            if not soTien:
                return Response({"error": "Thiếu thông tin số tiền."}, status=status.HTTP_400_BAD_REQUEST)
            qs_baoung, _ = AdvanceType.objects.get_or_create(
                typecode="Báo ứng",
                need_operator=True,
                company=qs_com
            )
            qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
            create_request=AdvanceRequest.objects.create(company=qs_com,
                                requester=qs_res,
                                requesttype=qs_baoung,
                                operator=operator,
                                amount=soTien,
                                comment=lyDo,
                                request_date= request.data.get('ngayUng',None),
                                hinhthucThanhtoan= request.data.get('hinhthucThanhtoan',None),
                                nguoiThuhuong= request.data.get('nguoiThuhuong',None),
                                khacCtk= request.data.get('khacCtk',None),
                                khacNganhang= request.data.get('khacNganhang',None),
                                khacStk= request.data.get('khacStk',None),
                            )
            created_data=AdvanceRequestSerializer(create_request).data
            AdvanceRequestHistory.objects.create(request=create_request,
                                                user=qs_res,action="create",
                                                old_data=None,
                                                new_data=f"{created_data}",
                                                comment="Khởi tạo")
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except company.DoesNotExist:
            return Response({"detail": "Không tìm thấy công ty tương ứng."}, status=status.HTTP_404_NOT_FOUND)
        except company_staff.DoesNotExist:
            return Response({"detail": "Người dùng không thuộc công ty hoặc chưa kích hoạt."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"detail": f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def nghiviec(self, request, pk=None):
        ngaynghi = request.data.get('ngayNghi',now())
        lyDo = request.data.get('lyDo',None)
        try:
            # xóa cty đang làm, cập nhập lịch sử làm việc tại công ty đang làm
            operator = self.get_object()
            hist=operator_history.objects.filter(operator=operator).order_by('-id')
            if len(hist)==0:
                return Response({"detail": f"Nhân viên {operator.ho_ten} chưa đi làm ở công ty nào!"}, status=status.HTTP_400_BAD_REQUEST)
            ctyNow=hist.first()
            if datetime.strptime(ngaynghi,"%Y-%m-%d").replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")) < ctyNow.start_date:
                return Response({"detail": "Ngày nghỉ phải lớn hơn ngày bắt đầu làm!"}, status=status.HTTP_400_BAD_REQUEST)
            if ctyNow.end_date:
                operator.congty_danglam = None
                return Response({"detail": f"Nhân viên {operator.ho_ten} đang không đi làm!"}, status=status.HTTP_400_BAD_REQUEST)
            ctyNow.end_date=ngaynghi
            ctyNow.reason=lyDo
            operator.congty_danglam = None
            ctyNow.save()
            operator.save()
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_create(self, serializer):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res = company_staff.objects.get(
            user__user=user,
            isActive=True,
            company__key=key
        )
        serializer.save(
            company=qs_res.company,
            nguoibaocao=qs_res
        )
        
    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            instance = self.get_object()
            qs_res = company_staff.objects.get(
                user__user=user,
                isActive=True,
                company__key=key
            )
            if not qs_res:
                return Response(
                    {"detail": "Bạn không có quyền!"}, status=status.HTTP_403_FORBIDDEN
                )
            if instance.nguoituyen==qs_res or instance.nguoibaocao==qs_res:
                with transaction.atomic():
                    updated_instance=super().partial_update(request, *args, **kwargs)
                    instance.refresh_from_db()
                    return Response(CompanyOperatorMoreDetailsSerializer(instance).data, 
                                status=status.HTTP_200_OK)
            return Response(
                {"detail": "Bạn không có quyền!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Không tìm thấy dữ liệu!"}, status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError as e:
            IntegrityErrorLog.objects.create(
                models_name="company_operator",
                api_name="CompanyOperatorViewSet",
                error_message=str(e),
                endpoint=request.path,
                payload=request.data
            )
            return Response(
                {"detail": "Lỗi cập nhập!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def create(self, request, *args, **kwargs):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            qs_res = company_staff.objects.get(
                user__user=user,
                isActive=True,
                company__key=key
            )
            if qs_res:
                with transaction.atomic():
                    request.data["nguoibaocao"]=qs_res.id
                    if request.data.get("ma_nhanvien") is None:
                        request.data["ma_nhanvien"]=f"RANDOM_{uuid.uuid4().hex.upper()[:12]}"
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    user_create = serializer.save(company=qs_res.company)
                    return Response(CompanyOperatorMoreDetailsSerializer(user_create).data, status=201)
            else:
                return Response(
                    {"detail": "Bạn không có quyền!"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except IntegrityError as e:
            IntegrityErrorLog.objects.create(
                models_name="company_operator",
                api_name="CompanyOperatorViewSet",
                error_message=str(e),
                endpoint=request.path,
                payload=request.data
            )
            if 'UNIQUE constraint failed' in str(e):
                name=request.data.get("ma_nhanvien")
                return Response(
                    {"detail": f"Mã nhân viên {name} đã tồn tại!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"detail": "Lỗi khởi tạo!"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
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
    
class CompanyOperatorDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOperatorDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company_operator.objects.filter(company=qs_res.company)
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
    
class CompanyOperatorMoreDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOperatorMoreDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company_operator.objects.filter(company=qs_res.company)
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
    
class CompanySublistViewSet(viewsets.ModelViewSet):
    serializer_class = companySublistSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return company.objects.filter(id=qs_res.company.id)
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
class AdvanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = AdvanceRequestSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get','post']
    
    @action(methods=['get'], detail=False, url_path='config', url_name='config')
    def getconfig(self, request):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        company=qs_res.company
        qs_type=AdvanceType.objects.filter(company=company)
        qs_reason=AdvanceReasonType.objects.filter(company=company)
        qs_op = company_operator.objects.filter(
            Q(nguoituyen=qs_res) | Q(nguoibaocao=qs_res),
            company=qs_res.company
        )
        return Response(data={
            "phanloai":AdvanceTypeSerializer(qs_type,many=True).data,
            "lydo":AdvanceReasonTypeSerializer(qs_reason,many=True).data,
            "nguoilaodong":CompanyOperatorSerializer(qs_op,many=True).data
        }, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            qs_res = company_staff.objects.get(user__user=user,isActive=True,company__key=key)
            rs_type=request.data["reasonType"]
            if not rs_type:
                return Response(
                    {"detail": "Chưa chọn lý do!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            rs_yeucau=request.data["yeucau"]
            if not rs_yeucau:
                return Response(
                    {"detail": "Chưa chọn lý do!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            rs_op=request.data.get('nguoilaodong',None)
            if qs_res and rs_type:
                try:
                    qs_rstype=AdvanceReasonType.objects.get(id=rs_type)
                    qs_type=AdvanceType.objects.get(id=rs_yeucau)
                    qs_op=None if rs_op==None else company_operator.objects.get(id=rs_op)
                    with transaction.atomic():
                        create=AdvanceRequest.objects.create(
                            company=qs_res.company,
                            requester=qs_res,
                            requesttype=qs_type,
                            reason=qs_rstype,
                            operator=qs_op,
                            comment=request.data.get('reason',None),
                            amount=request.data.get('amount',None),
                            request_date= request.data.get('date',datetime.now().date()),
                            hinhthucThanhtoan= request.data.get('payType',None),
                            nguoiThuhuong= request.data.get('owner',"staff"),
                            khacCtk= request.data.get('khacCtk',None),
                            khacNganhang= request.data.get('khacNganhang',None),
                            khacStk= request.data.get('khacStk',None),
                        )
                        created_data=AdvanceRequestSerializer(create).data
                        AdvanceRequestHistory.objects.create(request=create,
                                                            user=qs_res,action="create",
                                                            old_data=None,
                                                            new_data=f"{created_data}",
                                                            comment="Khởi tạo")
                        return Response(created_data, status=status.HTTP_200_OK)
                except AdvanceReasonType.DoesNotExist:
                    return Response(
                        {"detail": "Lý do không hợp lệ!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except AdvanceType.DoesNotExist:
                    return Response(
                        {"detail": "Yêu cầu không hợp lệ!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except company_operator.DoesNotExist:
                    return Response(
                        {"detail": "Người lao động không hợp lệ!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except IntegrityError as e:
            print(f"{str(e)}")
            IntegrityErrorLog.objects.create(
                models_name="company_operator",
                api_name="CompanyOperatorViewSet",
                error_message=str(e),
                endpoint=request.path,
                payload=request.data
            )
            return Response(
                {"detail": "Lỗi khởi tạo!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
                
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        return AdvanceRequest.objects.filter(company=qs_res.company)

    @action(detail=True, methods=['post'])
    def approved(self, request, pk=None):
        adv=self.get_object()
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=company_staff.objects.get(user__user=user,isActive=True,company__key=key)
        comment = request.data.get('comment',None)
        # kiểm tra quyền
        try:
            adv.status="approved"
            adv.approver=user
            adv.payment_status="done"
            adv.save()
            AdvanceRequestHistory.objects.create(request=adv,user=qs_res,
                                                action="approved",comment=comment)
            return Response(AdvanceRequestDetailsSerializer(adv).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, *args, **kwargs):
        """Tùy chỉnh GET /id/ nếu cần"""
        instance = self.get_object()
        data = AdvanceRequestDetailsSerializer(instance).data
        return Response(data, status=status.HTTP_200_OK)
    
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