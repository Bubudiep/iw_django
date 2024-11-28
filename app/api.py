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
from rest_framework.exceptions import AuthenticationFailed, NotFound
from django.db.models import Count
import time
from django.db import transaction
import uuid  # Thư viện để tạo khóa ngẫu nhiên
from geopy.distance import geodesic
import random
from .socket import send_socket
from django.db.models import Q

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 9999
    
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

class QR_loginAPIView(APIView):
    def post(self, request):
        data = request.data
        try:
            platform=data.get("platform",None);
            app=data.get("app",None);
            print(f"{platform}_{app}")
            qs_app=Fixed_link.objects.get(platform=platform,app=app)
            create_key=QR_Login.objects.create(isSuccess=False)
            print(app)
            return Response({
                "link":qs_app.link,
                "key":create_key.QRKey
            }, status=status.HTTP_201_CREATED)
        except Tang.DoesNotExist:
            return Response({'Error': "Không tìm thấy tầng"}, status=status.HTTP_404_NOT_FOUND)
        except Phong.DoesNotExist:
            return Response({'Error': "Không tìm thấy phòng"}, status=status.HTTP_404_NOT_FOUND)
        except Nhatro.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"Error":f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
 
def log_user_action(user, action_type, menu_item=None, search_term=None, category=None,restaurant_item=None):
    UserActionLog.objects.create(
        user=user,
        action_type=action_type,
        menu_item=menu_item,
        search_term=search_term,
        category=category,
        restaurant_item=restaurant_item,
        created_at=timezone.now()
    )
       
class UpdateSocketAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            try:
                data = request.data
                qs_profile=Profile.objects.get(user=request.user)
                qs_profile.socket_id=data.get("socket",None)
                qs_profile.save()
                return Response(data={"result":"PASS"},status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={"result":"FAIL"},status=status.HTTP_403_FORBIDDEN)
            
class RemoveSocketAPIView(APIView):
    def post(self, request):
        data = request.data
        if data.get("socket",None) is not None:
            try:
                qs_profile=Profile.objects.get(socket_id=data.get("socket"))
                qs_profile.socket_id=None
                qs_profile.save()
                return Response(data={"result":"PASS"},status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={"result":"FAIL"},status=status.HTTP_403_FORBIDDEN)


class UserAcceptItemOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                user = request.user
                item_id=data.get("items",None)
                can=data.get("can",None)
                qs_item=Restaurant_order_items.objects.get(id=item_id)
                if qs_item.Order.user_order!=user:
                    return Response(data={"Error":"Bạn không phải chủ bàn!"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if can==True:
                        qs_item.is_accept=True
                    if can==False:
                        qs_item.is_rejected=True
                    qs_item.save()
                    qs_profile=Profile.objects.filter(user=qs_item.user_order).values_list("socket_id",flat=True)
                    data_socket={
                        "send_to":list(qs_profile),
                        "type":"order",
                        "from":"offline",
                        "action":"join-res",
                        "order_key":qs_item.Order.OrderKey,
                        "data":Restaurant_order_detailsSerializer(qs_item.Order).data
                    }
                    send_socket("backend-enduser-event",data_socket)
                    return Response(data={
                        "result":"PASS",
                        "data":Restaurant_order_detailsSerializer(qs_item.Order).data
                    },status=status.HTTP_200_OK)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
                return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"Error":"Yêu cầu đăng nhập!"}, status=status.HTTP_403_FORBIDDEN)
class UserCreateOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                user = request.user
                item_id=data.get("items",None)
                qty=data.get("qty",None)
                coupon=data.get("coupon",None)
                phone=data.get("userphone",None)
                address=data.get("address",None)
                notes=data.get("notes",None)
                time=data.get("time",None)
                is_use_coupon=False
                takeaway=data.get("takeaway",None)
                if takeaway is not None:
                    is_takeaway=True
                    items=data.get("items",None)
                    notes=data.get("notes",None)
                    restaurant=data.get("restaurant",None)
                    groupId=data.get("groupId",None)
                    spaceId=data.get("spaceId",None)
                    with transaction.atomic():
                        qs_restaurant=Restaurant.objects.get(id=restaurant)
                        qs_space=None
                        qs_group=None
                        cr_oder=None
                        if spaceId is not None:
                            is_takeaway=False
                            try:
                                qs_user_table=Restaurant_space.objects.filter(user_use=user,is_inuse=True).exclude(id=spaceId)
                                if len(qs_user_table)>0:
                                    return Response(data={"Error":"Bạn đang sử dụng một bàn khác"}, status=status.HTTP_400_BAD_REQUEST)
                                qs_space=Restaurant_space.objects.get(id=spaceId,is_active=True)
                                qs_group=qs_space.group
                                if qs_space is not None and is_takeaway==False:
                                    if qs_space.is_inuse==True and qs_space.user_use!=user:
                                        if data.get("join",None) is not None:
                                            cr_oder=Restaurant_order.objects.filter(restaurant=qs_restaurant,
                                                                                    user_order=data.get("join",None),
                                                                                    space=qs_space).first()
                                            for item in items:
                                                qs_item=Restaurant_menu_items.objects.get(id=item.get("id"))
                                                if qs_item.is_delete==True:
                                                    return Response(data={"Error":f"{qs_item.name} đã bị xóa!"},
                                                                    status=status.HTTP_400_BAD_REQUEST)
                                                if qs_item.is_active==False:
                                                    return Response(data={"Error":f"{qs_item.name} đã bị gỡ xuống!"},
                                                                    status=status.HTTP_400_BAD_REQUEST)
                                                if qs_item.is_available==False:
                                                    return Response(data={"Error":f"{qs_item.name} hiện không khả dụng!"},
                                                                    status=status.HTTP_400_BAD_REQUEST)
                                                cr_item=Restaurant_order_items.objects.create(Order=cr_oder,
                                                                                            items=qs_item,
                                                                                            user_order=user,
                                                                                            price=qs_item.price,
                                                                                            is_accept=False,
                                                                                            name=qs_item.name,
                                                                                            quantity=item.get("quantity"))
                                            qs_profile=Profile.objects.filter(user__id=data.get("join",None)).values_list("socket_id",flat=True)
                                            data_socket={
                                                "send_to":list(qs_profile),
                                                "type":"order",
                                                "from":"offline",
                                                "action":"join",
                                                "order_key":cr_oder.OrderKey,
                                                "data":Restaurant_order_detailsSerializer(cr_oder).data
                                            }
                                            send_socket("backend-enduser-event",data_socket)
                                            return Response(data={
                                                "result":"PASS",
                                                "data":Restaurant_order_detailsSerializer(cr_oder).data
                                            },status=status.HTTP_200_OK)
                                        else:
                                            return Response(data={"Error":"Bàn đang được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)
                                    if qs_space.is_inuse==True and qs_space.user_use==user:
                                        # Bàn vẫn đang đc sử dụng bởi người này
                                        cr_oder=Restaurant_order.objects.filter(restaurant=qs_restaurant,
                                                                                    user_order=user,
                                                                                    space=qs_space).first()
                                        cr_oder.status="RECEIVED"
                                        cr_oder.is_paid=False
                                        cr_oder.is_clear=False
                                        cr_oder.is_paided=False
                                        cr_oder.save()
                                    qs_space.is_inuse=True
                                    qs_space.user_use=user
                                    qs_space.save()
                                       
                                # lấy những order đang ở trên quầy của người này tại bàn này và 
                            except Restaurant_space.DoesNotExist:
                                return Response(data={"Error":"Vị trí bàn không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)
                        qs_old_order=Restaurant_order.objects.filter(restaurant=qs_restaurant,user_order=user,status="CREATED")
                        if len(qs_old_order)>=3:
                            return Response(data={"Error":"Tối đa 3 đơn hàng chờ duyệt"}, status=status.HTTP_400_BAD_REQUEST)
                        if cr_oder is None:
                            cr_oder=Restaurant_order.objects.create(OrderKey=uuid.uuid4().hex.upper(),
                                                                restaurant=qs_restaurant,
                                                                user_order=user,
                                                                status="CREATED",
                                                                is_use_coupon=is_use_coupon,
                                                                is_online=False,
                                                                is_takeaway=is_takeaway,
                                                                space=qs_space,
                                                                group=qs_group,
                                                                is_paid=False,
                                                                is_paided=False,
                                                                custom_notes=notes)
                        for item in items:
                            qs_item=Restaurant_menu_items.objects.get(id=item.get("id"))
                            if qs_item.is_delete==True:
                                return Response(data={"Error":f"{qs_item.name} đã bị xóa!"},
                                                status=status.HTTP_400_BAD_REQUEST)
                            if qs_item.is_active==False:
                                return Response(data={"Error":f"{qs_item.name} đã bị gỡ xuống!"},
                                                status=status.HTTP_400_BAD_REQUEST)
                            if qs_item.is_available==False:
                                return Response(data={"Error":f"{qs_item.name} hiện không khả dụng!"},
                                                status=status.HTTP_400_BAD_REQUEST)
                            cr_item=Restaurant_order_items.objects.create(Order=cr_oder,
                                                                        items=qs_item,
                                                                        price=qs_item.price,
                                                                        name=qs_item.name,
                                                                        quantity=item.get("quantity"))
                        qs_staff=Restaurant_staff.objects.filter(restaurant=qs_item.menu.restaurant,
                                                                is_Active=True).values_list("user__id",flat=True)
                        qs_profile=Profile.objects.filter(user__id__in=qs_staff).values_list("socket_id",flat=True)
                        alert=LenmonAlert.objects.create(is_private=True,
                                                        user=user,alert_type="oder",
                                                        alert_sub_type="create",
                                                        title="Đặt hàng",
                                                        message="Bạn đã đặt hàng thành công!",
                                                        target_type="key",
                                                        target=cr_oder.OrderKey,
                                                        is_checked=False)
                        data_socket={
                            "send_to":list(qs_profile),
                            "type":"order",
                            "from":"offline",
                            "action":"create",
                            "order_key":cr_oder.OrderKey,
                            "data":Restaurant_order_detailsSerializer(cr_oder).data
                        }
                        send_socket("backend-enduser-event",data_socket)
                        return Response(data={
                            "result":"PASS",
                            "data":Restaurant_order_detailsSerializer(cr_oder).data
                        },status=status.HTTP_200_OK)
                if item_id is not None and qty is not None and address is not None:
                    qs_item=Restaurant_menu_items.objects.get(id=item_id)
                    if coupon is not None:
                        ...
                        # qs_coupon=
                    if qs_item.is_delete==True:
                        return Response(data={"Error":"Sản phẩm đã bị xóa!"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if qs_item.is_active==False:
                        return Response(data={"Error":"Sản phẩm đã bị gỡ xuống!"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if qs_item.is_available==False:
                        return Response(data={"Error":"Sản phẩm hiện không khả dụng!"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if qs_item.is_online==False:
                        return Response(data={"Error":"Sản phẩm không cho đặt online!"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    cr_oder=Restaurant_order.objects.create(OrderKey=uuid.uuid4().hex.upper(),
                                                            restaurant=qs_item.menu.restaurant,
                                                            user_order=user,
                                                            status="CREATED",
                                                            is_use_coupon=is_use_coupon,
                                                            is_online=True,
                                                            is_paid=False,
                                                            is_paided=False,
                                                            custom_notes=notes,
                                                            custom_phone=phone,
                                                            custom_address=address.get("all",None),
                                                            custom_lat=address.get("lat",None),
                                                            custom_long=address.get("lon",None),
                                                            custom_time=time)
                    cr_item=Restaurant_order_items.objects.create(Order=cr_oder,
                                                                items=qs_item,
                                                                price=qs_item.price,
                                                                name=qs_item.name,
                                                                quantity=qty)
                    qs_staff=Restaurant_staff.objects.filter(restaurant=qs_item.menu.restaurant,
                                                             is_Active=True).values_list("user__id",flat=True)
                    qs_profile=Profile.objects.filter(user__id__in=qs_staff).values_list("socket_id",flat=True)
                    alert=LenmonAlert.objects.create(is_private=True,
                                                     user=user,alert_type="oder",
                                                     alert_sub_type="CREATED",
                                                     title="Đặt hàng",
                                                     message="Bạn đã đặt hàng thành công!",
                                                     target_type="key",
                                                     target=cr_oder.OrderKey,
                                                     is_checked=False)
                    data_socket={
                        "send_to":list(qs_profile),
                        "type":"order",
                        "from":"online",
                        "action":"create",
                        "order_key":cr_oder.OrderKey,
                        "data":Restaurant_order_detailsSerializer(cr_oder).data
                    }
                    send_socket("backend-enduser-event",data_socket)
                    return Response(data={
                        "result":"PASS",
                        "data":Restaurant_order_detailsSerializer(cr_oder).data
                    },status=status.HTTP_200_OK)
                else:
                    return Response(data={"Error":"Thiếu dữ liệu!"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
                return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"Error":"Yêu cầu đăng nhập!"}, status=status.HTTP_403_FORBIDDEN)
            
class ResPaidOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                order_id=data.get("id",None);
                donban=data.get("donban",None);
                try:
                    qs_order=Restaurant_order.objects.get(id=order_id)
                    qs_admin=Restaurant_staff.objects.get(user=request.user,is_Active=True,
                                restaurant=qs_order.restaurant)
                    
                    if donban and qs_order.space is not None:
                        qs_order.space.is_inuse=False
                        qs_order.is_clear=True
                        qs_order.is_paided=True
                        qs_order.space.user_use=None
                        qs_order.space.save()
                        qs_order.save()
                        if qs_order.status=="COMPLETE":
                            return Response(data={
                                        "result":"PASS", 
                                        "data":Restaurant_order_detailsSerializer(qs_order).data
                                    },status=status.HTTP_200_OK)
                    order=Restaurant_order_items.objects.filter(Order=qs_order)
                    for od in order:
                        od.is_paid=True
                        od.save()
                    if qs_order.status=="COMPLETE" or qs_order.status=="NOT" or qs_order.status=="CANCEL":
                        return Response(data={"Error":"Trạng thái hiện tại đã hoàn tất"},status=status.HTTP_400_BAD_REQUEST)
                    if qs_order.status=="CREATED":
                        return Response(data={"Error":"Chưa nhận đơn hàng"},status=status.HTTP_400_BAD_REQUEST)
                    if qs_order.status=="RECEIVED":
                        return Response(data={"Error":"Chưa giao đơn"},status=status.HTTP_400_BAD_REQUEST)
                    if qs_order.status=="DELIVERED" or qs_order.status=="PAIDING":
                        qs_order.status = "COMPLETE"
                        qs_order.is_paided=True
                        qs_order.save()
                        alert=LenmonAlert.objects.create(is_private=True,
                                                        user=qs_order.user_order,alert_type="oder",
                                                        alert_sub_type="COMPLETE",
                                                        title="Thanh toán",
                                                        message="Thanh toán đơn hàng thành công!",
                                                        target_type="key",
                                                        target=qs_order.OrderKey,
                                                        is_checked=False)
                        isfrom="offline"
                        if qs_order.is_online==True:
                            isfrom="online"
                        qs_profile=Profile.objects.get(user=qs_order.user_order)
                        print(f"{qs_profile.socket_id}")
                        data_socket={
                            "send_to":[qs_profile.socket_id],
                            "type":"order",
                            "from":isfrom,
                            "action":"COMPLETE",
                            "order_key":qs_order.OrderKey,
                            "data":Restaurant_order_detailsSerializer(qs_order).data
                        }
                        send_socket("backend-enduser-event",data_socket)
                    return Response(data={
                                    "result":"PASS", 
                                    "data":Restaurant_order_detailsSerializer(qs_order).data
                                },status=status.HTTP_200_OK)
                except Restaurant_order.DoesNotExist:
                    return Response(data={"Error":"Không thấy order"},status=status.HTTP_400_BAD_REQUEST)
                except Restaurant_staff.DoesNotExist:
                    return Response(data={"Error":"Bạn không phải nhân viên của quán"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                res_data = generate_response_json("Error", f"[{file_name}_{lineno}] {str(e)}")
                return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
   
class ResDeliveryOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                order_id=data.get("id",None);
                itemIds=data.get("itemIds",None);
                is_giao=data.get("is_giao",None);
                try:
                    qs_order=Restaurant_order.objects.get(id=order_id)
                    qs_admin=Restaurant_staff.objects.get(user=request.user,is_Active=True,
                                restaurant=qs_order.restaurant)
                    if qs_order.status=="COMPLETE" or qs_order.status=="NOT" or qs_order.status=="CANCEL":
                        return Response(data={"Error":"Trạng thái hiện tại đã hoàn tất"},status=status.HTTP_400_BAD_REQUEST)
                    if qs_order.status=="CREATED":
                        return Response(data={"Error":"Chưa nhận đơn hàng"},status=status.HTTP_400_BAD_REQUEST)
                    for item in itemIds:
                        qs_item=Restaurant_order_items.objects.get(id=item,Order=qs_order)
                        if qs_item.status=='WAIT':
                            if is_giao==True:
                                qs_item.status="DONE"
                            elif is_giao==False:
                                qs_item.status="CANCEL"
                        qs_item.save()
                    if not Restaurant_order_items.objects.filter(Order=qs_order, status="WAIT").exists():
                        qs_order.status = "DELIVERED"
                        qs_order.save()
                        alert=LenmonAlert.objects.create(is_private=True,
                                                        user=qs_order.user_order,alert_type="oder",
                                                        alert_sub_type="DELIVERED",
                                                        title="Giao hàng",
                                                        message="Hoàn thành đơn hàng!",
                                                        target_type="key",
                                                        target=qs_order.OrderKey,
                                                        is_checked=False)
                        isfrom="offline"
                        if qs_order.is_online==True:
                            isfrom="online"
                        qs_profile=Profile.objects.get(user=qs_order.user_order)
                        print(f"{qs_profile.socket_id}")
                        data_socket={
                            "send_to":[qs_profile.socket_id],
                            "type":"order",
                            "from":isfrom,
                            "action":"DELIVERED",
                            "order_key":qs_order.OrderKey,
                            "data":Restaurant_order_detailsSerializer(qs_order).data
                        }
                        send_socket("backend-enduser-event",data_socket)
                    return Response(data={
                                    "result":"PASS", 
                                    "data":Restaurant_order_detailsSerializer(qs_order).data
                                },status=status.HTTP_200_OK)
                except Restaurant_order.DoesNotExist:
                    return Response(data={"Error":"Không thấy order"},status=status.HTTP_400_BAD_REQUEST)
                except Restaurant_staff.DoesNotExist:
                    return Response(data={"Error":"Bạn không phải nhân viên của quán"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                res_data = generate_response_json("Error", f"[{file_name}_{lineno}] {str(e)}")
                return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
            
class ResAcceptOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                order_id=data.get("id",None);
                try:
                    qs_order=Restaurant_order.objects.get(id=order_id)
                    qs_admin=Restaurant_staff.objects.get(user=request.user,is_Active=True,
                                restaurant=qs_order.restaurant)
                    if qs_order.status=="COMPLETE" or qs_order.status=="NOT" or qs_order.status=="CANCEL":
                        return Response(data={"Error":"Trạng thái hiện tại đã hoàn tất"},status=status.HTTP_400_BAD_REQUEST)
                    if qs_order.status=="CREATED":
                        qs_order.status="RECEIVED"
                    qs_order.save()
                    alert=LenmonAlert.objects.create(is_private=True,
                                                    user=qs_order.user_order,alert_type="oder",
                                                    alert_sub_type="RECEIVED",
                                                    title="Đặt hàng",
                                                    message="Đơn hàng của bạn đã được chấp nhận!",
                                                    target_type="key",
                                                    target=qs_order.OrderKey,
                                                    is_checked=False)
                    isfrom="offline"
                    if qs_order.is_online==True:
                        isfrom="online"
                    qs_profile=Profile.objects.get(user=qs_order.user_order)
                    print(f"{qs_profile.socket_id}")
                    data_socket={
                        "send_to":[qs_profile.socket_id],
                        "type":"order",
                        "from":isfrom,
                        "action":"RECEIVED",
                        "order_key":qs_order.OrderKey,
                        "data":Restaurant_order_detailsSerializer(qs_order).data
                    }
                    send_socket("backend-enduser-event",data_socket)
                    return Response(data={
                                    "result":"PASS", 
                                    "data":Restaurant_order_detailsSerializer(qs_order).data
                                },status=status.HTTP_200_OK)
                except Restaurant_order.DoesNotExist:
                    return Response(data={"Error":"Không thấy order"},status=status.HTTP_400_BAD_REQUEST)
                except Restaurant_staff.DoesNotExist:
                    return Response(data={"Error":"Bạn không phải nhân viên của quán"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                res_data = generate_response_json("Error", f"[{file_name}_{lineno}] {str(e)}")
                return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
            

class UserPaidOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                order_id=data.get("id",None);
                qs_order=Restaurant_order.objects.get(id=order_id,user_order=request.user)
                qs_order.is_paid=True
                qs_order.save()
                qs_staff=Restaurant_staff.objects.filter(restaurant=qs_order.restaurant,
                                                            is_Active=True).values_list("user__id",flat=True)
                qs_profile=Profile.objects.filter(user__id__in=qs_staff).values_list("socket_id",flat=True)
                isfrom="offline"
                if qs_order.is_online==True:
                    isfrom="online"
                if qs_order.is_paided==False:
                    data_socket={
                        "send_to":list(qs_profile),
                        "type":"order",
                        "from":isfrom,
                        "action":"paid",
                        "order_key":qs_order.OrderKey,
                        "data":Restaurant_order_detailsSerializer(qs_order).data
                    }
                    send_socket("backend-enduser-event",data_socket)
                return Response(data={"result":"PASS",
                                      "data":Restaurant_order_detailsSerializer(qs_order).data},status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={"Error":"Xảy ra lỗi khi cập nhập"},status=status.HTTP_403_FORBIDDEN)
            
class UserCancelOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                order_id=data.get("id",None);
                qs_order=Restaurant_order.objects.get(id=order_id,user_order=request.user)
                if qs_order.status=="COMPLETE" or qs_order.status=="NOT" or qs_order.status=="CANCEL":
                    return Response(data={"Error":"Trạng thái hiện tại đã hoàn tất"},status=status.HTTP_403_FORBIDDEN)
                if qs_order.status=="CREATED":
                    qs_order.cancel_status="CREATED"
                    qs_order.status="CANCEL"
                if qs_order.status=="SHIPPING":
                    qs_order.cancel_status="SHIPPING"
                    qs_order.status="CANCEL"
                if qs_order.status=="RECEIVED":
                    qs_order.cancel_status="RECEIVED"
                    qs_order.status="CANCEL"
                if qs_order.space:
                    qs_order.space.is_inuse=False
                    qs_order.space.user_use=None
                    qs_order.space.save()
                    qs_order.is_clear=True
                    qs_order.space=None
                qs_order.save()
                
                qs_staff=Restaurant_staff.objects.filter(restaurant=qs_order.restaurant,
                                                            is_Active=True).values_list("user__id",flat=True)
                qs_profile=Profile.objects.filter(user__id__in=qs_staff).values_list("socket_id",flat=True)
                isfrom="offline"
                if qs_order.is_online==True:
                    isfrom="online"
                data_socket={
                    "send_to":list(qs_profile),
                    "type":"order",
                    "from":isfrom,
                    "action":"CANCEL",
                    "order_key":qs_order.OrderKey,
                    "data":Restaurant_order_detailsSerializer(qs_order).data
                }
                send_socket("backend-enduser-event",data_socket)
                return Response(data={"result":"PASS"},status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={"Error":"Xảy ra lỗi khi cập nhập"},status=status.HTTP_403_FORBIDDEN)
            
class UserActionLogAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
        try:
            user = request.user  # user hiện tại từ request
            action_type=data.get("type",None) #like/follow
            action_is=data.get("action",None) #yes/no
            target=data.get("target",None) #restaurant/menu_item
            items=data.get("item",None) #id of item
            if action_type is not None and action_is is not None and target is not None and items is not None:
                if target=="restaurant": #nhà hàng
                    qs_res=Restaurant.objects.get(id=items)
                    if action_is=="yes":
                        qs_his=UserLikeLog.objects.filter(user=user,
                                                        restaurant_item=qs_res,
                                                        action_type=action_type)
                        if len(qs_his)==0:
                            log_user_like(user=user,
                                        action_type=action_type,
                                        restaurant_item=qs_res,
                                        menu_item=None)
                        return Response(data={"Pass":f"Đã {action_type}","data":True}, status=status.HTTP_200_OK)
                    if action_is=="no":
                        qs_his=UserLikeLog.objects.filter(user=user,
                                                        restaurant_item=qs_res,
                                                        action_type=action_type)
                        for log in qs_his:
                            log.delete()
                        return Response(data={"Pass":f"Đã hủy {action_type}","data":False}, status=status.HTTP_200_OK)
                elif target=="menu_item": #item
                    qs_item=Restaurant_menu_items.objects.get(id=items)
                    if action_is=="yes":
                        qs_his=UserLikeLog.objects.filter(user=user,
                                                        menu_item=qs_item,
                                                        action_type=action_type)
                        if len(qs_his)==0:
                            log_user_like(user=user,
                                        action_type=action_type,
                                        menu_item=qs_item,
                                        restaurant_item=None)
                        return Response(data={"Pass":f"Đã {action_type}","data":True}, status=status.HTTP_200_OK)
                    if action_is=="no":
                        qs_his=UserLikeLog.objects.filter(user=user,
                                                        menu_item=qs_item,
                                                        action_type=action_type)
                        for log in qs_his:
                            log.delete()
                        return Response(data={"Pass":f"Đã hủy {action_type}","data":False}, status=status.HTTP_200_OK)
                else:
                    return Response(data={"Error":"Chưa hỗ trợ hạng mục này"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"Error":"Chưa đủ thông tin"}, status=status.HTTP_400_BAD_REQUEST)
        except Restaurant.DoesNotExist:
            return Response(data={"Error":"Không tìm thấy nhà hàng này"}, status=status.HTTP_400_BAD_REQUEST)
        except Restaurant_menu_items.DoesNotExist:
            return Response(data={"Error":"Không tìm thấy sản phẩm này"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
        
def log_user_like(user, action_type, menu_item=None,restaurant_item=None):
    UserLikeLog.objects.create(
        user=user,
        action_type=action_type,
        menu_item=menu_item,
        restaurant_item=restaurant_item,
        created_at=timezone.now()
    )
# log_user_action(user=request.user, action_type='click', menu_item=selected_menu_item)
# log_user_action(user=request.user, action_type='search', search_term=search_query)
# log_user_action(user=request.user, action_type='category_view', category=selected_category)
def get_popular_menu_items(user): # Được bấm vào nhiều nhất
    popular_items = UserActionLog.objects.filter(action_type='click') \
                    .values('menu_item') \
                    .annotate(click_count=Count('menu_item')) \
                    .order_by('-click_count')[:6]
    if len(popular_items)>0:
        return Restaurant_menu_items.objects.filter(id__in=[item['menu_item'] for item in popular_items],
                                                    is_delete=False,is_active=True,
                                                    is_validate=True,name__isnull=False,
                                                    image64_mini__isnull=False,
                                                    image64_full__isnull=False
                                                )
    else:
        if user is not None:
            list_group=get_user_favorite_categories(user)
            print(list_group)
            return Restaurant_menu_items.objects.filter(group__name__in=list_group
                                                        ,is_delete=False,is_active=True,
                                                        is_validate=True,name__isnull=False,
                                                        image64_mini__isnull=False,
                                                        image64_full__isnull=False
                                                        ).order_by('?')[:6]
        else:
            list_group=get_user_favorite_categories(None)
            print(list_group)
            return Restaurant_menu_items.objects.filter(group__name__in=list_group
                                                        ,is_delete=False,is_active=True,
                                                        is_validate=True,name__isnull=False,
                                                        image64_mini__isnull=False,
                                                        image64_full__isnull=False
                                                        ).order_by('?')[:6]

def get_popular_search_terms(): # Phổ biến tìm kiếm
    popular_searches = UserActionLog.objects.filter(action_type='search') \
                       .values('search_term') \
                       .annotate(search_count=Count('search_term')) \
                       .order_by('-search_count')[:5]
    return [term['search_term'] for term in popular_searches]

def get_user_favorite_categories(user):  # Lấy danh mục phổ biến nhất của người dùng
    # Lọc các mục UserActionLog theo user và loại hành động là 'click'
    if user is not None:
        favorite_categories = UserActionLog.objects.filter(user=user, action_type='click', menu_item__isnull=False) \
                            .values('menu_item__group') \
                            .annotate(count=Count('menu_item__group')) \
                            .order_by('-count')[:6]  # Lấy 5 mục phổ biến nhất
    else: 
        favorite_categories = UserActionLog.objects.filter(action_type='click', menu_item__isnull=False) \
                            .values('menu_item__group') \
                            .annotate(count=Count('menu_item__group')) \
                            .order_by('-count')[:6]  # Lấy 5 mục phổ biến nhất   
    if favorite_categories:
        categories = []
        for category in favorite_categories:
            try:
                group_id = category['menu_item__group']
                if group_id is not None:
                    group = Restaurant_menu_groups.objects.get(id=group_id)
                    categories.append(group.name)
            except Restaurant_menu_groups.DoesNotExist:
                print(f"Group with ID {group_id} does not exist.")
                categories.append(None)  # Add None or a default value if not found
            except Exception as e:
                print(f"An error occurred: {e}")
                categories.append(None)  # Add None or handle the error gracefully
        return categories

    # Nếu không có dữ liệu, lấy 5 danh mục ngẫu nhiên từ Restaurant_menu_groups
    all_categories = list(Restaurant_menu_groups.objects.all())
    if all_categories:
        random_categories = random.sample(all_categories, min(5, len(all_categories)))  # Lấy tối đa 5 danh mục ngẫu nhiên
        return [category.name for category in random_categories]

    return []  # Nếu không có danh mục nào trong database, trả về danh sách rỗng
def get_nearby_favorite_category(user_latitude, user_longitude, radius_km=25):
    # Lấy tất cả các hành động nhấn vào món ăn từ người dùng khác
    nearby_users_actions = UserActionLog.objects.filter(action_type='click', menu_item__isnull=False)
    # Lọc các người dùng có vị trí gần người dùng hiện tại
    nearby_categories = []
    for action in nearby_users_actions:
        if hasattr(action.user, 'profile') and action.user.profile.lat_pos and action.user.profile.long_pos:
            # Lấy tọa độ của người dùng từ profile
            action_lat = float(action.user.profile.lat_pos)
            action_long = float(action.user.profile.long_pos)
            # Tính khoảng cách giữa người dùng hiện tại và người dùng hành động
            user_coords = (user_latitude, user_longitude)
            action_coords = (action_lat, action_long)
            distance = geodesic(user_coords, action_coords).kilometers
            # Nếu người dùng đó nằm trong bán kính cho phép, thêm vào danh mục của họ
            if distance <= radius_km:
                nearby_categories.append(action.menu_item.group)
    # Đếm số lượng danh mục để tìm danh mục phổ biến nhất
    if nearby_categories:
        popular_category = (
            UserActionLog.objects.filter(menu_item__group__in=nearby_categories)
            .values('menu_item__group')
            .annotate(category_count=Count('menu_item__group'))
            .order_by('-category_count')
            .first()
        )
        if popular_category:
            return Restaurant_menu_groups.objects.get(id=popular_category['menu_item__group']).name
    return None  # Trả về None nếu không tìm thấy danh mục nào

def get_nearby_restaurants(user, user_latitude, user_longitude, radius_km=25):
    favorite_category = get_user_favorite_categories(user)  # Sử dụng hàm này từ code trước để lấy danh mục yêu thích của người dùng
    # Nếu người dùng không có danh mục yêu thích, trả về danh sách rỗng
    if not favorite_category:
        favorite_category=get_nearby_favorite_category(user_latitude, user_longitude, radius_km)
        if not favorite_category:
            return []
    # Lấy các nhà hàng có chứa danh mục yêu thích của người dùng
    nearby_restaurants = []
    restaurants = Restaurant.objects.filter(is_active=True)  # Lọc các nhà hàng đang hoạt động
    for restaurant in restaurants:
        # Kiểm tra nếu nhà hàng có danh mục yêu thích của người dùng
        qs_menu=Restaurant_menu_groups.objects.filter(menu__restaurant=restaurant, name=favorite_category)
        if Restaurant_menu_groups.objects.filter(menu__restaurant=restaurant, name__in=favorite_category).exists():
            # Lấy tọa độ của nhà hàng từ address_details
            address_details = restaurant.address_details
            if address_details and 'lat' in address_details and 'long' in address_details:
                restaurant_coords = (address_details['lat'], address_details['long'])
                user_coords = (user_latitude, user_longitude)
                # Tính khoảng cách giữa người dùng và nhà hàng
                distance = geodesic(user_coords, restaurant_coords).kilometers
                # Kiểm tra nếu nhà hàng nằm trong bán kính cho phép
                if distance <= radius_km:
                    nearby_restaurants.append({
                        "restaurant": restaurant,
                        "distance_km": round(distance, 2)
                    })
    return sorted(nearby_restaurants, key=lambda x: x['distance_km'])

class RetaurantNearlyAPIView(APIView):  # Các nhà hàng ở gần
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = []  # Không yêu cầu xác thực, xử lý riêng trong logic
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        user_latitude = request.query_params.get('latitude', None)
        user_longitude = request.query_params.get('longitude', None)
        # Nếu có vị trí, xử lý tìm nhà hàng gần
        if user_latitude is not None and user_longitude is not None:
            user_latitude = float(user_latitude)
            user_longitude = float(user_longitude)
            # Đăng nhập: Lấy danh mục yêu thích cá nhân của người dùng
            if user:
                favorite_category = get_user_favorite_categories(user)
            else:
                # Không đăng nhập: Lấy danh mục phổ biến gần vị trí
                favorite_category = get_nearby_favorite_category(user_latitude, user_longitude)
            # Gợi ý nhà hàng gần vị trí
            nearby_restaurants = get_nearby_restaurants(user, user_latitude, user_longitude)
            if len(nearby_restaurants)==0:
                # Nếu không có vị trí, trả về danh sách ngẫu nhiên
                random_restaurants = self.get_random_restaurants()
                suggestions = {
                    "nearby_restaurants": random_restaurants,
                    "favorite_category": None  # Không có danh mục yêu thích nếu không cung cấp vị trí
                }
            suggestions = {
                "nearby_restaurants": [
                    {
                        "id": item["restaurant"].id,
                        "name": item["restaurant"].name,
                        "address": item["restaurant"].address,
                        "avatar": item["restaurant"].avatar,
                        "phone_number": item["restaurant"].phone_number,
                        "distance_km": item["distance_km"]
                    }
                    for item in nearby_restaurants
                ],
                "favorite_category": favorite_category
            }
            return Response(suggestions)
        # Nếu không có vị trí, trả về danh sách ngẫu nhiên
        random_restaurants = self.get_random_restaurants()
        suggestions = {
            "nearby_restaurants": random_restaurants,
            "favorite_category": None  # Không có danh mục yêu thích nếu không cung cấp vị trí
        }
        return Response(suggestions)

    def get_random_restaurants(self):
        """Lấy 4 nhà hàng ngẫu nhiên từ cơ sở dữ liệu, nếu có ít hơn 4 thì lấy tất cả"""
        all_restaurants = list(Restaurant.objects.all())
        num_restaurants_to_get = min(4, len(all_restaurants))  # Đảm bảo không lấy quá số nhà hàng có sẵn
        random_restaurants = random.sample(all_restaurants, num_restaurants_to_get)
        
        return [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "phone_number": restaurant.phone_number,
                "avatar": restaurant.avatar,
                "distance_km": None  # Không tính khoảng cách nếu không có vị trí
            }
            for restaurant in random_restaurants
        ]        
class MyListOrderAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        if request.user.is_authenticated:
            user=request.user
            result = {}
            for status_code, status_display in Restaurant_order.ORDER_STATUS_CHOICES:
                total_count = Restaurant_order.objects.filter(status=status_code,
                                                              user_order=user).count()
                recent_orders = Restaurant_order.objects.filter(status=status_code,
                                                                user_order=user).order_by('-created_at')[:3]
                result[status_code] = {
                    "status_code": status_code,
                    "status_display": status_display,
                    "total_count": total_count,
                    "recent_orders": [
                        {
                            "id":order.id,
                            "OrderKey": order.OrderKey,
                            "restaurant": order.restaurant.name,
                            "is_paid": order.is_paid,
                            "is_paided": order.is_paided,
                            "custom_notes":order.custom_notes,
                            "created_at": order.created_at,
                            "updated_at": order.updated_at,
                            "items": [
                                {
                                    "name": item.name,
                                    "price": item.price,
                                    "quantity": item.quantity,
                                    "created_at": item.created_at,
                                    "updated_at": item.updated_at,
                                }
                                for item in Restaurant_order_items.objects.filter(Order=order)
                            ],
                        }
                        for order in recent_orders
                    ],
                }
            
            return Response(result, status=200)
        else:
            return Response({"detail": "Authentication required."}, status=401)
            
class LenmonNewsItemsAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = []  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        new=Restaurant_menu_items.objects.filter(
            is_online=True,
            is_active=True,
            is_delete=False,
            menu__is_online=True,
            name__isnull=False, # phải có tên
            image64_mini__isnull=False, #phải có ảnh đại diện
            is_validate=True, # phải được phê duyệt
        )[:6]
        return Response(Restaurant_menu_itemsSTSerializer(new,many=True).data,
                        status=status.HTTP_200_OK)
            
class RestaurantMenuItemsViewSet(viewsets.ModelViewSet):
    queryset = Restaurant_menu_items.objects.all()
    serializer_class = Restaurant_menu_itemsSTSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = []
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']

    def get_queryset(self):
        # Lọc các món ăn từ nhiều quán khác nhau
        diverse_items=Restaurant_menu_items.objects.filter(
            is_active=True,
            is_delete=False,
            is_available=True,
            name__isnull=False, # phải có tên
            image64_mini__isnull=False, #phải có ảnh đại diện
            is_validate=True, # phải được phê duyệt
        ).order_by('?')
        return diverse_items
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
    
class RecommendItemsAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = []  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            popular_items = get_popular_menu_items(user)
            popular_search_terms = get_popular_search_terms()
            favorite_category = get_user_favorite_categories(user)
            suggestions = {
                "popular_items": Restaurant_menu_itemsRCMSerializer(popular_items,many=True).data,
                "popular_search_terms": popular_search_terms,
                "user_favorite_category": favorite_category,
            }
            return Response(suggestions,status=status.HTTP_200_OK)
        else:
            popular_items = get_popular_menu_items(None)
            popular_search_terms = get_popular_search_terms()
            favorite_category = get_user_favorite_categories(None)
            suggestions = {
                "popular_items": Restaurant_menu_itemsRCMSerializer(popular_items,many=True).data,
                "popular_search_terms": popular_search_terms,
                "user_favorite_category": favorite_category,
            }
            return Response(suggestions,status=status.HTTP_200_OK)
            
class CreateRestaurantAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
        try:
            user = request.user  # user hiện tại từ request
            print(data)
            with transaction.atomic():
                # tạo nhà hàng
                option=data.get("option")
                restaurant=Restaurant.objects.create(name=data.get("name"),
                                                address=data.get("address"),
                                                phone_number=data.get("phone"),
                                                mohinh=data.get("mohinh"),
                                                avatar=data.get("avatar"),
                                                Takeaway=option.get("Oder"),
                                                isRate=option.get("Rate"),
                                                isChat=option.get("Chat"),
                                                Oder_online=option.get("OderOnline"))
                menu=Restaurant_menu.objects.create(restaurant=restaurant,name="Default")
                # Tạo các "mark" (đánh dấu)
                marks = [
                    Restaurant_menu_marks(menu=menu, name="Mới"),
                    Restaurant_menu_marks(menu=menu, name="Tiêu biểu"),
                ]
                Restaurant_menu_marks.objects.bulk_create(marks)

                # Tạo các "group" (nhóm)
                groups = [
                    Restaurant_menu_groups(menu=menu, name="Món chính"),
                    Restaurant_menu_groups(menu=menu, name="Món phụ"),
                    Restaurant_menu_groups(menu=menu, name="Món gọi thêm"),
                    Restaurant_menu_groups(menu=menu, name="Nước uống"),
                    Restaurant_menu_groups(menu=menu, name="Ăn vặt"),
                    Restaurant_menu_groups(menu=menu, name="Món gọi kèm"),
                    Restaurant_menu_groups(menu=menu, name="Khác"),
                ]
                Restaurant_menu_groups.objects.bulk_create(groups)
                room=Restaurant_socket.objects.create(restaurant=restaurant,
                                                      QRKey=uuid.uuid4().hex.upper())
                staff=Restaurant_staff.objects.create(user=user,
                                                restaurant=restaurant,
                                                is_Admin=True,is_Active=True)
                layout = Restaurant_layout.objects.create(
                    restaurant=restaurant,
                    name=f"Tầng 1"
                )
                for room_number, table_count in data.get("table", {}).items():
                    group = Restaurant_space_group.objects.create(
                        layout=layout,
                        name=f"Phòng {room_number}"
                    )
                    for table_index in range(1, table_count + 1):
                        Restaurant_space.objects.create(
                            layout=layout,
                            group=group,
                            name=f"Bàn {table_index}",
                            description=f"Bàn số {table_index} trong phòng {room_number}",
                        )
                        
                qs_staff=Restaurant_staff.objects.filter(user=user,
                                    is_Active=True).values_list("restaurant__id",
                                    flat=True)
                restaurants = Restaurant.objects.filter(id__in=qs_staff)
                return Response({
                    "count":len(restaurants),
                    "data":RestaurantDetailsSerializer(restaurants,many=True).data
                }, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà hàng"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_403_FORBIDDEN)
                
class LenmonAppAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def get(self, request):
        if request.user.is_authenticated:
            data = request.data
        try:
            user = request.user  # user hiện tại từ request
            qs_staff=Restaurant_staff.objects.filter(user=user,is_Active=True).values_list("restaurant__id",flat=True)
            print(qs_staff)
            restaurants = Restaurant.objects.filter(id__in=qs_staff)
            for rest in restaurants:
                qs_socket=Restaurant_socket.objects.filter(restaurant=rest)
                if len(qs_socket)==0:
                    socket=Restaurant_socket.objects.create(restaurant=rest,QRKey=uuid.uuid4().hex.upper())
                    socket.save()
            return Response({
                "count":len(restaurants),
                "data":RestaurantDetailsSerializer(restaurants,many=True).data
            }, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà hàng"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_403_FORBIDDEN)
        
class ThemnguoivaoAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            soPhong=data.get("phong",None)
            if soPhong is None:
                return Response({'Error': "Chưa nhập số phòng"}, status=status.HTTP_400_BAD_REQUEST)
            tenTang=data.get("tang",None)
            if tenTang is None:
                return Response({'Error': "Chưa nhập tên tầng"}, status=status.HTTP_400_BAD_REQUEST)
            qs_phong=Phong.objects.get(
                id=soPhong, 
                tang__id=tenTang, 
                tang__nhaTro__user=request.user
            )
            qs_old=LichsuNguoitro.objects.filter(phong=qs_phong,nguoiTro__cccd=data.get("cccd", None),
                                                ngayBatdauO__isnull=False,
                                                ngayKetthucO__isnull=True)
            if len(qs_old)>0:
                return Response({'Error': "Người này đã có trong phòng trọ!"}, status=status.HTTP_404_NOT_FOUND)
            nguoitro= Nguoitro.objects.create(
                cccd=data.get("cccd", None),
                hoTen=data.get("hoTen", None),
                sdt=data.get("sdt", None),
                quequan=data.get("quequan", None),
                ngaysinh=data.get("ngaySinh", None)
            )
            lichsu_otro=LichsuNguoitro.objects.create(nguoiTro=nguoitro,
                                            phong=qs_phong,
                                            ngayBatdauO=data.get("ngayBatDau", None),
                                            tiencoc=data.get("tienCoc", None))
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
            qs_profile=Profile.objects.get(user=request.user)
            qs_old=Nhatro.objects.filter(user=request.user)
            if qs_profile.level is None or qs_profile.level==0:
                if len(qs_old)>0:
                    return Response({"Error":"Số nhà trọ đã đến giới hạn!"}, status=status.HTTP_400_BAD_REQUEST)
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
    
class NhatroUpdateAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            phong=data.get("phong",None)
            if phong is None:
                return Response({'Error': "Chưa chọn nhà trọ"}, status=status.HTTP_400_BAD_REQUEST)
            giaphong=data.get("giaphong",None)
            if giaphong is None:
                return Response({'Error': "Chưa chọn nhà trọ"}, status=status.HTTP_400_BAD_REQUEST)
            sodien=data.get("sodien",None)
            if sodien is None:
                return Response({'Error': "Chưa nhập số phòng"}, status=status.HTTP_400_BAD_REQUEST)
            sonuoc=data.get("sonuoc",None)
            if sonuoc is None:
                return Response({'Error': "Chưa nhập tên tầng"}, status=status.HTTP_400_BAD_REQUEST)
            wifi=data.get("wifi",None)
            if wifi is None:
                return Response({'Error': "Bạn đang sử dụng phiên bản khác"}, status=status.HTTP_400_BAD_REQUEST)
            dieuhoa=data.get("dieuhoa",None)
            if dieuhoa is None:
                return Response({'Error': "Bạn đang sử dụng phiên bản khác"}, status=status.HTTP_400_BAD_REQUEST)
            nonglanh=data.get("nonglanh",None)
            if nonglanh is None:
                return Response({'Error': "Bạn đang sử dụng phiên bản khác"}, status=status.HTTP_400_BAD_REQUEST)
            qs_phong=Phong.objects.get(id=phong,tang__nhaTro__user=request.user)
            qs_phong.giaPhong=giaphong
            qs_phong.wifi=wifi
            qs_phong.giaDien=data.get("tiendien",qs_phong.giaDien)
            qs_phong.giaNuoc=data.get("tiennuoc",qs_phong.giaNuoc)
            qs_phong.giaRac=data.get("tienrac",qs_phong.giaRac)
            qs_phong.giaKhac=data.get("tienkhac",qs_phong.giaKhac)
            qs_phong.dieuhoa=dieuhoa
            qs_phong.nonglanh=nonglanh
            qs_phong.save()
            tieuthu=LichsuTieuThu.objects.create(phong=qs_phong,
                                                soDienKetthuc=sodien,
                                                soNuocKetthuc=sonuoc)
            qs_nhatro=Nhatro.objects.filter(user=request.user)
            return Response({
                "phong":PhongSerializer(qs_phong,many=False).data,
                "tro_hientai":NhatroDetailsSerializer(qs_phong.tang.nhaTro,many=False).data,
                "tro":NhatroDetailsSerializer(qs_nhatro,many=True).data
            }, status=status.HTTP_201_CREATED)
        except Phong.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class XacnhanTamtruAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            phongtro=data.get("phongtro",None)
            if phongtro is None:
                return Response({'Error': "Lỗi không xác định"}, status=status.HTTP_400_BAD_REQUEST)
            qs_ptro=LichsuNguoitro.objects.get(id=phongtro)
            nguoitro=qs_ptro.nguoiTro
            nguoitro.tamtru=True
            nguoitro.save()
            qs_tro=Nhatro.objects.filter(user=request.user)
            return Response({
                "lichsu":LichsuNguoitroSerializer(qs_ptro,many=False).data,
                "nhatro":NhatroDetailsSerializer(qs_tro,many=True).data
            }, status=status.HTTP_201_CREATED)
        except LichsuNguoitro.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class KiemtraTroAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.query_params.get('KEY', None)
        print(key)
        if key:
            try:
                qs_nhatro=Nhatro.objects.get(QRKey=key)
                return Response(Nhatro_thongtinSerializer(qs_nhatro).data, status=status.HTTP_200_OK)
            except Nhatro.DoesNotExist:
                return Response({"error": "Không thấy nhà trọ!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "KEY parameter is missing or invalid."}, status=status.HTTP_400_BAD_REQUEST)
    
class XacnhanThanhtoanAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            hoadon=data.get("hoadon",None)
            sotien=data.get("sotien",None)
            ghichu=data.get("ghichu",None)
            qs_hoadon=LichsuThanhToan.objects.get(id=hoadon,phong__tang__nhaTro__user=request.user)
            qs_old=ChiTietThanhToan.objects.filter(lichsu_thanh_toan=qs_hoadon)
            dathanhtoan=0
            for thanhtoan in qs_old:
                dathanhtoan+=thanhtoan.so_tien
            qs_nguoitro=LichsuNguoitro.objects.filter(phong=qs_hoadon.phong,
                                                      ngayBatdauO__isnull=False,
                                                      ngayKetthucO__isnull=True,
                                                      isOnline=True)
            thanhtoan=ChiTietThanhToan.objects.create(nguoiTro=qs_nguoitro.first().nguoiTro,
                                                    lichsu_thanh_toan=qs_hoadon,
                                                    so_tien=sotien,
                                                    ghichu=ghichu)
            dathanhtoan+=int(sotien)
            if dathanhtoan>=int(qs_hoadon.tongTien):
                qs_hoadon.ngayThanhToan=datetime.datetime.now()
                qs_hoadon.isPaid=True
                qs_hoadon.save()
            qs_tro=Nhatro.objects.filter(user=request.user)
            return Response(NhatroDetailsSerializer(qs_tro,many=True).data, status=status.HTTP_201_CREATED)
        except Phong.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class NhatroThanhtoanAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def post(self, request):
        data = request.data
        # Kiểm tra token đã xác thực
        if request.user.is_authenticated:
            data = request.data
        try:
            soDien=data.get("soDien",None)
            soNuoc=data.get("soNuoc",None)
            phong=data.get("phong",None)
            soTienPhong=data.get("soTienPhong",None)
            soTienDien=data.get("soTienDien",None)
            soTienNuoc=data.get("soTienNuoc",None)
            soTienWifi=data.get("soTienWifi",None)
            soTienRac=data.get("soTienRac",None)
            soTienKhac=data.get("soTienKhac",None)
            tongTien=data.get("tongTien",None)
            ngayBatdau=data.get("ngayBatdau",None)
            ngayKetthuc=data.get("ngayKetthuc",None)
            qs_phong=Phong.objects.get(id=phong,tang__nhaTro__user=request.user)
            thanhtoan=LichsuThanhToan.objects.create(user=request.user,
                                                    phong=qs_phong,
                                                    soTienPhong=soTienPhong,
                                                    soTienDien=soTienDien,
                                                    soTienNuoc=soTienNuoc,
                                                    soTienWifi=soTienWifi,
                                                    soTienRac=soTienRac,
                                                    soTienKhac=soTienKhac,
                                                    tongTien=tongTien,
                                                    ngayBatdau=ngayBatdau,
                                                    ngayKetthuc=ngayKetthuc)
            tieuthu=LichsuTieuThu.objects.create(hoadon=thanhtoan,
                                                phong=qs_phong,
                                                soDienKetthuc=soDien,
                                                soNuocKetthuc=soNuoc,
                                                ngaBatdau=ngayKetthuc,
                                                ngayKetthuc=ngayKetthuc)
            qs_tro=Nhatro.objects.filter(user=request.user)
            return Response(NhatroDetailsSerializer(qs_tro,many=True).data, status=status.HTTP_201_CREATED)
        except Phong.DoesNotExist:
            return Response({'Error': "Không tìm thấy nhà trọ"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

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
        zalo_phone = request.data.get('zalo_phone',None)
        zalo_name = request.data.get('zalo_name',None)
        zalo_avatar = request.data.get('zalo_avatar',None)

        try:
            if not zalo_id:
                return Response({'detail': 'Zalo ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Xác thực người dùng qua zalo_id
            profile = get_object_or_404(Profile, zalo_id=zalo_id)
            if zalo_name is not None and profile.zalo_name!=zalo_name:
                profile.zalo_name=zalo_name
            if zalo_avatar is not None and profile.zalo_avatar!=zalo_avatar:
                profile.zalo_avatar=zalo_avatar
            if (profile.zalo_phone is None or profile.zalo_phone.strip()=="") and zalo_phone is not None:
                profile.zalo_phone=zalo_phone
            profile.save()
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
            key = request.data.get('key',None)
            valid_token = existing_tokens.filter(expires__gt=now).first()
            if valid_token:
                if key is not None:
                    try:
                        qs_key=QR_Login.objects.get(QRKey=key)
                        if qs_key:
                            send_socket("backend-event",{
                                "token":valid_token.token,
                                "expires_in":int((valid_token.expires - now).total_seconds()),
                                "room":qs_key.QRKey,
                                "status":"PASS"
                            })
                            qs_key.user=user
                            qs_key.isSuccess=True
                            qs_key.save()
                    except QR_Login.DoesNotExist:
                        return Response({'Error': 'Có lỗi xảy ra!'}, status=status.HTTP_403_FORBIDDEN)
                return JsonResponse({
                    'access_token': valid_token.token,
                    'expires_in': int((valid_token.expires - now).total_seconds()),
                    'token_type': 'Bearer',
                    'scope': valid_token.scope,
                    'refresh_token': 'existing_refresh_token',  # Add your logic to handle refresh tokens
                    'user':UserSerializer(user,many=False).data
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
            if key is not None:
                qs_key=QR_Login.objects.get(QRKey=key)
                if qs_key:
                    send_socket("backend-event",{
                        "token":access_token_str,
                        "expires_in":expires_in_seconds,
                        "room":qs_key.QRKey,
                        "status":"PASS"
                    })
                    qs_key.user=user
                    qs_key.isSuccess=True
                    qs_key.save()
            return JsonResponse({
                'access_token': access_token_str,
                'expires_in': expires_in_seconds,
                'token_type': 'Bearer',
                'scope': 'read write',
                'refresh_token': refresh_token_str,
                'user':UserSerializer(user,many=False).data
            })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
   
class ZaloLogin_Lemon_APIView(APIView):
    def post(self, request):
        zalo_id = request.data.get('zalo_id')
        zalo_phone = request.data.get('zalo_phone',None)
        zalo_name = request.data.get('zalo_name',None)
        zalo_avatar = request.data.get('zalo_avatar',None)

        if not zalo_id:
            return Response({'detail': 'Zalo ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Xác thực người dùng qua zalo_id
        profile = get_object_or_404(Profile, zalo_id=zalo_id)
        if zalo_name is not None and profile.zalo_name!=zalo_name:
            profile.zalo_name=zalo_name
        if zalo_avatar is not None and profile.zalo_avatar!=zalo_avatar:
            profile.zalo_avatar=zalo_avatar
        if (profile.zalo_phone is None or profile.zalo_phone.strip()=="") and zalo_phone is not None:
            profile.zalo_phone=zalo_phone
        profile.save()
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
        key = request.data.get('key',None)
        valid_token = existing_tokens.filter(expires__gt=now).first()
        if valid_token:
            if key is not None:
                qs_key=QR_Login.objects.get(QRKey=key)
                if qs_key:
                    send_socket("backend-event",{
                        "token":valid_token.token,
                        "expires_in":int((valid_token.expires - now).total_seconds()),
                        "room":qs_key.QRKey,
                        "status":"PASS"
                    })
                    qs_key.user=user
                    qs_key.isSuccess=True
                    qs_key.save()
            return JsonResponse({
                'access_token': valid_token.token,
                'expires_in': int((valid_token.expires - now).total_seconds()),
                'token_type': 'Bearer',
                'scope': valid_token.scope,
                'refresh_token': 'existing_refresh_token',  # Add your logic to handle refresh tokens
                'user':UserLenmonSerializer(user,many=False).data
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
        if key is not None:
            qs_key=QR_Login.objects.get(QRKey=key)
            if qs_key:
                send_socket("backend-event",{
                    "token":access_token_str,
                    "expires_in":expires_in_seconds,
                    "room":qs_key.QRKey,
                    "status":"PASS"
                })
                qs_key.user=user
                qs_key.isSuccess=True
                qs_key.save()
        return JsonResponse({
            'access_token': access_token_str,
            'expires_in': expires_in_seconds,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': refresh_token_str,
            'user':UserSerializer(user,many=False).data
        })
    
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile=Profile.objects.get(user=user)
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
                    'access_token': token.token,
                    'expires_in': expires_in_seconds,
                    'token_type': 'Bearer',
                    'scope': 'read write',
                    'refresh_token': refresh_token_str,
                    'user':UserSerializer(user,many=False).data
                })
            except Exception as e:
                return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                 
class TokenLoginAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            qs_app = Application.objects.first()
            expires_in_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 360000)
            now = timezone.now()
            existing_tokens = AccessToken.objects.filter(user=user, application=qs_app)
            for token in existing_tokens:
                if token.expires < now:
                    token.delete()
            valid_token = existing_tokens.filter(expires__gt=now).first()
            if valid_token:
                return JsonResponse({
                    'access_token': valid_token.token,
                    'expires_in': int((valid_token.expires - now).total_seconds()),
                    'token_type': 'Bearer',
                    'scope': valid_token.scope,
                    'refresh_token': 'existing_refresh_token',  # Add your logic to handle refresh tokens
                    'user':UserLenmonSerializer(user,many=False).data
                })
            else:
                expires_at = now + timedelta(seconds=expires_in_seconds)
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
                return JsonResponse({
                    'access_token': access_token_str,
                    'expires_in': expires_in_seconds,
                    'token_type': 'Bearer',
                    'scope': 'read write',
                    'refresh_token': refresh_token_str,
                    'user':UserSerializer(user,many=False).data
                })
                
class LenmonRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data=request.data
        profile=Profile.objects.filter(zalo_name=data.get("zalo_name"),
                                     zalo_phone=data.get("zalo_phone"))
        if len(profile)==1:
            user = profile[0].user
            qs_app = Application.objects.first()
            expires_in_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 360000)
            now = timezone.now()
            existing_tokens = AccessToken.objects.filter(user=user, application=qs_app)
            for token in existing_tokens:
                if token.expires < now:
                    token.delete()
            valid_token = existing_tokens.filter(expires__gt=now).first()
            if valid_token:
                return JsonResponse({
                    'access_token': valid_token.token,
                    'expires_in': int((valid_token.expires - now).total_seconds()),
                    'token_type': 'Bearer',
                    'scope': valid_token.scope,
                    'refresh_token': 'existing_refresh_token',  # Add your logic to handle refresh tokens
                    'user':UserLenmonSerializer(user,many=False).data
                })
            expires_at = now + timedelta(seconds=expires_in_seconds)
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
            return JsonResponse({
                'access_token': access_token_str,
                'expires_in': expires_in_seconds,
                'token_type': 'Bearer',
                'scope': 'read write',
                'refresh_token': refresh_token_str,
                'user':UserSerializer(user,many=False).data
            })
        serializer = LenmonRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile=Profile.objects.get(user=user)
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
                    'access_token': token.token,
                    'expires_in': expires_in_seconds,
                    'token_type': 'Bearer',
                    'scope': 'read write',
                    'refresh_token': refresh_token_str,
                    'user':UserSerializer(user,many=False).data
                })
            except Exception as e:
                return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChuyencaAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            id_nhanvien=request.data.get("id",None)
            calamviec=request.data.get("calamviec",None)
            ngayapdung=request.data.get("ngayapdung",None)
            ghichu=request.data.get("ghichu",None)
            if ngayapdung is None:
                ngayapdung=datetime.datetime.now()
            qs_profile=Profile.objects.get(user=user)
            qs_admin=DanhsachAdmin.objects.filter(zalo_id=qs_profile.zalo_id).values_list("id",flat=True)
            qs_nvien=DanhsachNhanvien.objects.get(congty__id__in=qs_admin,id=id_nhanvien)
            nghiviec=request.data.get("nghiviec",None)
            if nghiviec is not None:
                his=DanhsachNhanvien_record.objects.create(nhanvien=qs_nvien,
                                                            user=user,column='nghiviec',
                                                            ngayapdung=ngayapdung,
                                                            old_value=qs_nvien.nghiviec,
                                                            new_value=nghiviec,
                                                            ghichu=ghichu,
                                                        )
                qs_nvien.nghiviec=nghiviec
                qs_nvien.save()
                return Response(DanhsachNhanvienSerializer(qs_nvien).data, status=status.HTTP_200_OK)
            his=DanhsachNhanvien_record.objects.create(nhanvien=qs_nvien,
                                                        user=user,column='calamviec',
                                                        ngayapdung=ngayapdung,
                                                        old_value=qs_nvien.calamviec,
                                                        new_value=calamviec,
                                                        ghichu=ghichu,
                                                    )
            qs_nvien.calamviec=calamviec
            qs_nvien.save()
            return Response(DanhsachNhanvienSerializer(qs_nvien).data, status=status.HTTP_200_OK)
        return Response({"Error":"Vui lòng đăng nhập"}, status=status.HTTP_401_UNAUTHORIZED)

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
        
        thismonth = self.request.query_params.get('thismonth')
        if thismonth is not None:
            today = datetime.date.today()
            current_month = today.month
            current_year = today.year
            queryset=queryset.filter(
                Q(ngaydilam__year=current_year) & Q(ngaydilam__month=current_month)
            )
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
           
class NhatroNoiquyViewSet(viewsets.ModelViewSet):
    serializer_class = NhatroNoiquySerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NhatroNoiquyFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['post','patch','get']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return NhatroNoiquy.objects.all()
        return NhatroNoiquy.objects.filter(nhaTro__user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Set the user field
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

class PhongViewSet(viewsets.ModelViewSet):
    serializer_class = PhongSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PhongFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['post','patch']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Phong.objects.all()
        return Phong.objects.filter(tang__nhaTro__user=user)

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

class DanhsachDilamViewSet(viewsets.ModelViewSet):
    serializer_class = DanhsachnhanvienDilamSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DanhsachnhanvienDilamFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['post']
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

class LichsuThanhToanViewSet(viewsets.ModelViewSet):
    serializer_class = LichsuThanhToanSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LichsuThanhToanFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['post']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return LichsuThanhToan.objects.all()
        return LichsuThanhToan.objects.filter(phong__tang__nhaTro__user=user)

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

class Restaurant_menu_itemsViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantMenuItemsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RestaurantMenuItemsFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['post','patch']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Restaurant_menu_items.objects.all()
        qs_res=Restaurant_staff.objects.filter(user=user,is_Active=True).values_list("restaurant__id",flat=True)
        return Restaurant_menu_items.objects.filter(menu__restaurant__id__in=qs_res)

    def create(self, request, *args, **kwargs):
        # Set the user to the authenticated user
        user = request.user  # Retrieve the authenticated user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            allowed_restaurants = Restaurant_staff.objects.filter(
                user=user,
                is_Active=True,
            ).values_list("restaurant__id",flat=True)
            qs_items=Restaurant_menu_items.objects.filter(
                menu=serializer.validated_data.get('menu'),
                is_delete=False
            )
            if qs_items.count() >= 25:
                return Response(
                    {"Error": "Tối đa 25 món trên một menu!"},
                    status=status.HTTP_403_FORBIDDEN
                )
            menu_restaurant_id = serializer.validated_data.get("menu").restaurant.id
            if menu_restaurant_id in allowed_restaurants:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"Error": "Bạn không có quyền!"},
                    status=status.HTTP_403_FORBIDDEN
                )
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

class Restaurant_spaceDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSpaceSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Restaurant_space.objects.all()
        qs_res=Restaurant_staff.objects.filter(user=user,is_Active=True).values_list("restaurant__id",flat=True)
        return Restaurant_space.objects.filter(
                group__layout__restaurant__in=qs_res
            )

    def retrieve(self, request, *args, **kwargs):
        # Lấy id từ kwargs
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        item_id = kwargs.get('pk')
        user = self.request.user
        menu_item = queryset.get(pk=item_id)
        serializer = self.get_serializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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

class Restaurant_menu_itemsDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantMenuItemsDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RestaurantMenuItemsFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Restaurant_menu_items.objects.all()
        return Restaurant_menu_items.objects.filter(
                is_delete=False,is_active=True
            )

    def retrieve(self, request, *args, **kwargs):
        # Lấy id từ kwargs
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        item_id = kwargs.get('pk')
        user = self.request.user
        try:
            menu_item = queryset.get(pk=item_id)
            fromClick = self.request.query_params.get('from')
            if fromClick is not None:
                log_user_action(user=user, action_type='click', menu_item=menu_item)
        except Restaurant_menu_items.DoesNotExist:
            raise NotFound(detail="Menu item not found", code=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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

class RestaurantViewViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantViewsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = []
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RestaurantFilter
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.is_superuser:
                return Restaurant.objects.all()
        return Restaurant.objects.filter(is_active=True)
    
    def retrieve(self, request, *args, **kwargs):
        # Lấy id từ kwargs
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        item_id = kwargs.get('pk')
        try:
            restaurant = queryset.get(pk=item_id)
            fromClick = self.request.query_params.get('from')
            if fromClick is not None:
                if self.request.user.is_authenticated:
                    log_user_action(user=self.request.user, action_type='click', restaurant_item=restaurant)
        except Restaurant.DoesNotExist:
            raise NotFound(detail="Restaurant not found", code=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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

class Restaurant_order_userViewSet(viewsets.ModelViewSet):
    serializer_class = Restaurant_orderSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Restaurant_orderFilter
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Restaurant_order.objects.all()
        return Restaurant_order.objects.filter(user_order=user)
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

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RestaurantFilter
    pagination_class = StandardResultsSetPagination
    # Chỉ cho phép GET
    http_method_names = ['patch']
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Restaurant_menu_items.objects.all()
        qs_res=Restaurant_staff.objects.filter(user=user,is_Active=True).values_list("restaurant__id",flat=True)
        return Restaurant.objects.filter(id__in=qs_res)

    def create(self, request, *args, **kwargs):
        # Set the user to the authenticated user
        user = request.user  # Retrieve the authenticated user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            allowed_restaurants = Restaurant_staff.objects.filter(
                user=user,
                is_Active=True,
            ).values_list("restaurant__id",flat=True)
            
            menu_restaurant_id = serializer.validated_data.get("menu").restaurant.id
            if menu_restaurant_id in allowed_restaurants:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "You do not have permission to create items for this restaurant."},
                    status=status.HTTP_403_FORBIDDEN
                )
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
    