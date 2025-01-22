import json
from django.shortcuts import render
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.utils.timezone import now
import pytz as tz
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
            zalo_id = request.data.get('zalo_id',None)
            key = request.headers.get('CompanyKey')
            try:
                company_instance=Company.objects.get(id=key)
                if zalo_id:
                  try:
                      prf=Profile.objects.get(zalo_id=zalo_id)
                      user=prf.user
                  except Exception as e:
                      if username:
                          user=Employee.objects.get(username=username,company=company_instance)
                          if check_password(password, user.password)==False:
                              return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
                      else:
                          return Response({'detail': 'Zalo id này chưa được liên kết'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                  if username:
                    user=Employee.objects.get(username=username,company=company_instance)
                    if check_password(password, user.password)==False:
                        return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
                if user.is_active==False:
                    return Response({'detail': 'Tài khoản của bạn đã bị khóa!'}, status=status.HTTP_403_FORBIDDEN)
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
        start_date_param = self.request.query_params.get('start_date')
        end_date_param = self.request.query_params.get('end_date')
        print(f"{start_date_param} - {end_date_param}")
        if start_date_param:
            try:
                start_date = datetime.strptime(start_date_param, "%Y-%m-%d")
                print(f"Start Date: {start_date}")  # In ra để kiểm tra giá trị
                queryset = queryset.filter(att_date__gte=start_date.date())
            except ValueError as e:
                print(f"Invalid start_date_param: {start_date_param}, Error: {e}")
                pass

        if end_date_param:
            try:
                end_date = datetime.strptime(end_date_param, "%Y-%m-%d")
                print(f"End Date: {end_date}")  # In ra để kiểm tra giá trị
                queryset = queryset.filter(att_date__lte=end_date.date())
            except ValueError as e:
                print(f"Invalid end_date_param: {end_date_param}, Error: {e}")
                pass
              
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

def add_minutes_to_time(dt, minutes=7):
    return dt + timedelta(minutes=minutes)
  
class AttendanceAPIView(APIView):
    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.data.get("data"))
        for att in json_data:
            if att.get('clock_in'):
                att['clock_in'] = datetime.strptime(att.get('clock_in'), '%Y-%m-%d %H:%M:%S.%f')
                att['clock_in'] = att['clock_in'].replace(tzinfo=pytz.timezone('Asia/Ho_Chi_Minh'))
                att['clock_in'] = add_minutes_to_time(att['clock_in'])

            if att.get('clock_out'):
                att['clock_out'] = datetime.strptime(att.get('clock_out'), '%Y-%m-%d %H:%M:%S.%f')
                att['clock_out'] = att['clock_out'].replace(tzinfo=pytz.timezone('Asia/Ho_Chi_Minh'))
                att['clock_out'] = add_minutes_to_time(att['clock_out'])

            if att.get('punch_time'):
                att['punch_time'] = datetime.strptime(att.get('punch_time'), '%Y-%m-%d %H:%M:%S.%f')
                att['punch_time'] = att['punch_time'].replace(tzinfo=pytz.timezone('Asia/Ho_Chi_Minh'))
                att['punch_time'] = add_minutes_to_time(att['punch_time'])
            try:
                emp=None
                qs_emp=Profile.objects.filter(emp_id=att.get("emp_code")).first()
                if qs_emp:
                  emp=qs_emp.user
                crt_punch=Punchtime.objects.get_or_create(id=att.get('punch_id'),
                                            defaults={
                                              'id' : att.get('punch_id'),
                                              'user' : emp,
                                              'punch_time' : att['punch_time'],
                                              'att_date' : att.get("att_date"),
                                              'emp_id' : att.get("emp_code")
                                            })[0]
                if crt_punch:
                    qs_old=Attendance.objects.filter(emp_id=att.get("emp_code"),att_date=att.get("att_date")).exclude(record_id=att.get("id"))
                    for old in qs_old:
                        old.delete()
                    qs_att = Attendance.objects.get_or_create(
                        record_id=att.get("id"),
                        defaults={
                            'user':emp,
                            'record_id': att.get("id"),
                            'emp_id': att.get("emp_code"),
                            'week': att.get("week"),
                            'weekday': att.get("weekday"),
                            'clock_in': att['clock_in'],
                            'clock_out': att['clock_out'],
                            'att_date': att.get("att_date"),
                        }
                    )[0]
                    qs_att.punch_time.add(crt_punch)
                    qs_att.save()
            except Exception as e:
              print(f"{e}")
              continue
        print("Hoàn tất!")
        return Response({"details":"Test"}, status=status.HTTP_200_OK)

class LatestPunchtimeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        latest_punchtime = Punchtime.objects.order_by('-punch_time').first()  # Sắp xếp giảm dần và lấy bản ghi đầu tiên
        if latest_punchtime:
            punch_time_value = latest_punchtime.punch_time
        else:
            punch_time_value = datetime(2024, 1, 1, 0, 0, 0)
        return Response({"data":punch_time_value}, status=status.HTTP_200_OK)