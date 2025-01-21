from django.shortcuts import render
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.utils.timezone import now
from .serializers import *
from rest_framework.filters import OrderingFilter
from django.db.models import Q,F
from oauth2_provider.models import AccessToken, Application
from django.contrib.auth.hashers import check_password
from oauthlib.common import generate_token
from oauth2_provider.settings import oauth2_settings
from datetime import timedelta, datetime
from oauth2_provider.models import RefreshToken
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 9999
# Create your views here.
class RegisterView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        key = request.headers.get('CompanyKey')
        user=self.request.user
        if user.is_authenticated:
          ...
        return Response({"error":"Chưa thể đăng ký"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            ip=get_client_ip(request)
            username = request.data.get('username')
            password = request.data.get('password')
            key = request.headers.get('CompanyKey')
            try:
                company_instance=Company.objects.get(id=key)
                user=Employee.objects.get(username=username,company=company_instance)
                if user.is_active==False:
                    return Response({'detail': 'Tài khoản của bạn đã bị khóa!'}, status=status.HTTP_403_FORBIDDEN)
                if check_password(password, user.password)==False:
                    return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            except Company.DoesNotExist:
                return Response({'detail': 'Công ty chưa được đăng ký'}, status=status.HTTP_401_UNAUTHORIZED)
            except Employee.DoesNotExist:
                return Response({'detail': 'Tài khoản không chính xác'}, status=status.HTTP_401_UNAUTHORIZED)
            application = Application.objects.all().first()
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
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            return Response({
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                'token_type': 'Bearer',
                'scope': access_token.scope,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
class UserView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        key = request.headers.get('CompanyKey')
        user=self.request.user
        if user.is_authenticated:
          qs_emp=Employee.objects.get(user=user)
          profile = Profile.objects.get_or_create(
              user=qs_emp,
              defaults={
                  'emp_id': user.username,
                  'full_name': None,
                  'deparment': None,
                  'zalo_id': None,
                  'zalo_number': None,
              }
          )[0]
          qs_ticket=AttendanceTicket.objects.filter(user=qs_emp)
          qs_mess=EmployeeMessage.objects.filter(user=qs_emp)
          current_date = timezone.now()
          current_month = current_date.month
          current_year = current_date.year
          # Kiểm tra nếu ngày hiện tại là 21 hoặc sau đó
          if current_date.day >= 21:
              # Nếu là ngày 21 hoặc sau đó, tháng lương là tháng sau
              month_salary = current_month + 1
              year_salary = current_year
              if month_salary > 12:  # Nếu tháng lương là tháng 13, thì chuyển sang tháng 1 năm sau
                  month_salary = 1
                  year_salary += 1
          else:
              # Nếu trước ngày 21, tháng lương là tháng hiện tại
              month_salary = current_month
              year_salary = current_year
          
          start_year = year_salary - 1 if month_salary == 1 else year_salary
          start_month = 12 if month_salary == 1 else month_salary - 1
          start_date = timezone.datetime(start_year, start_month, 21) 
          end_date = timezone.datetime(year_salary, month_salary, 20)
          
          # Lọc Attendance theo khoảng thời gian từ ngày 21 của tháng trước đến ngày 20 của tháng sau
          qs_att = Attendance.objects.filter(
              user=qs_emp,
              att_date__range=[start_date.date(), end_date.date()]
          )
          
          return Response({
            "ticket":{
              "total":len(qs_ticket),
              "uncheck":len(qs_ticket.filter(is_check=False))
            },
            "mess":{
              "total":len(qs_mess),
              "uncheck":len(qs_mess.filter(is_check=False))
            },
            "profile":UserProfileSerializer(profile).data,
            "attendance":UserAttendanceSerializer(qs_att,many=True).data
          }, status=status.HTTP_200_OK)
        return Response({"error":"Bạn không có quyền truy cập!"}, status=status.HTTP_400_BAD_REQUEST)
      
class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('CompanyKey')
        if user.is_superuser:
            return Attendance.objects.all()
        return Attendance.objects.filter(user__user=user)
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

class AttendanceAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AttendanceSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Chấm công được lưu thành công!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LatestPunchtimeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        latest_punchtime = Punchtime.objects.order_by('-punch_time').first()  # Sắp xếp giảm dần và lấy bản ghi đầu tiên
        if latest_punchtime:
            punch_time_value = latest_punchtime.punch_time
        else:
            punch_time_value = datetime(2024, 1, 1, 0, 0, 0)
        return Response({"data":punch_time_value}, status=status.HTTP_400_BAD_REQUEST)