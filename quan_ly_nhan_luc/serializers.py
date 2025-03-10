from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db import transaction
from django.db.models import Max,Sum,Q
from rest_framework.permissions import IsAuthenticated
from django.utils.functional import cached_property
import random
import string
import os
import sys
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from datetime import datetime
import pytz

def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 'x_forwarded_for' trả về danh sách IP cách nhau bởi dấu phẩy
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def record_user_action(function_name, action_name, staff, old_data=None, new_data=None, title=None, message=None, is_hidden=False, is_sended=False, is_received=False, is_readed=False):
    function = company_staff_history_function.objects.get_or_create(name=function_name)[0]
    action = company_staff_history_action.objects.get_or_create(name=action_name)[0]
    # Tạo history
    history = company_staff_history.objects.create(
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
    
class RegisterSerializer(serializers.ModelSerializer):
    # Bạn có thể thêm các trường zalo_name và zalo_id vào đây
    employeeCode = serializers.CharField(required=True)
    key = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    fullname = serializers.CharField(required=True)
    department = serializers.CharField(required=False)
    jobtitle = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['username','fullname', 'password', 'employeeCode','key','jobtitle','department']
        
    @cached_property
    def user(self):
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Không thể lấy thông tin người dùng từ request.")
        return request.user
    
    def create(self, validated_data):
        key = validated_data.pop('key', None)
        employeeCode = validated_data.pop('employeeCode',None)
        password = validated_data.pop('password',None)
        username = validated_data.pop('username',None)
        fullname = validated_data.pop('fullname',None)
        department = validated_data.pop('department',None)
        jobtitle = validated_data.pop('jobtitle',None)
        user = self.user
        qs_company=company.objects.get(key=key)
        print(f"{jobtitle} {department}")
        if not user.is_authenticated:
            raise serializers.ValidationError("Người dùng chưa được xác thực qua OAuth2")
        if key:
            try:
                qs_company=company.objects.get(key=key)
                qs_staff=company_staff.objects.get(company=qs_company,user__user=user)
                if qs_staff.isAdmin==False:
                    raise serializers.ValidationError({"Error":"Bạn không phải là admin!"})
            except company_staff.DoesNotExist:
                raise serializers.ValidationError({"Error":"Mã công ty không hợp lệ!"})
        else:
            raise serializers.ValidationError({"Error":"Mã công ty không hợp lệ!"})
        if employeeCode:
            qs_code=company_staff.objects.filter(company=qs_company,name=employeeCode)
            if len(qs_code)>0:
                raise serializers.ValidationError({"Error":"Mã nhân viên đã tồn tại!"})
        else:
            raise serializers.ValidationError({"Error":"Mã NV không được để trống!"})
        if department:
            try:
                department=company_department.objects.get(id=department,company=qs_company)
            except company_department.DoesNotExist:
                raise serializers.ValidationError({"Error":"Bộ phận không hợp lệ!"})
        if jobtitle:
            try:
                jobtitle=company_possition.objects.get(id=jobtitle,company=qs_company)
            except company_possition.DoesNotExist:
                raise serializers.ValidationError({"Error":"Chức vụ không hợp lệ!"})
        if username:
            qs_emp=company_account.objects.filter(username=username,company=qs_company)
            if len(qs_emp)>0:
                raise serializers.ValidationError({"Error":"Tài khoản đã tồn tại!"})
        if username and password:
            with transaction.atomic():
                newuser = User.objects.create_user(username=f"EMP_{qs_company.id}_{username}",
                                                password=''.join(random.choices(string.ascii_letters 
                                                                        + string.digits, k=12)))
                emp = company_account.objects.create(company=qs_company,user=newuser,
                                                    username=username, password=password)
                employee=company_staff.objects.create(company=qs_company,
                                                    name=employeeCode,
                                                    user=emp,
                                                    department=department,
                                                    possition=jobtitle,
                                                    isActive=True,
                                                    isSuperAdmin=False,
                                                    isAdmin=False,
                                                    isBan=False,
                                                    isOnline=False,
                                                    isValidate=False)
                profile=company_staff_profile.objects.create(staff=employee,
                                                             full_name=fullname)
                record_user_action(function_name="staff_account",action_name="create",staff=qs_staff,
                                   title="Công ty",message=f"Đã thêm tài khoản {employeeCode} thành công!",is_hidden=False)
                record_user_action(function_name="staff_account",action_name="create",staff=employee,
                                   title="Tài khoản",message="Tài khoản của bản đã được khởi tạo!",is_hidden=False)
        return emp
        
class companySerializer(serializers.ModelSerializer):
    class Meta:
        model = company
        fields = ['companyType','avatar','name','fullname','address',
        'addressDetails','hotline','isValidate','isOA','wallpaper',
        'shortDescription','description','created_at']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = company
        fields = ['companyType','avatar','name','fullname','address',
        'addressDetails','hotline','isValidate','isOA','wallpaper',
        'shortDescription','description','created_at']

class companyFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = company
        fields = '__all__'

class CompanyStaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_staff_profile
        fields = '__all__'

class CompanyStaffProfileLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = company_staff_profile
        fields = ['full_name','nick_name','avatar']

class CompanyStaffSmallSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)
    def get_profile(self, qs):
        try:
            profile=company_staff_profile.objects.get(staff=qs)
            return CompanyStaffProfileLTESerializer(profile).data
        except company_staff_profile.DoesNotExist:
            return None
    class Meta:
        model = company_staff
        fields = [
            'id','name','department',
            'possition','isSuperAdmin',
            'isActive','isAdmin',
            'isOnline','isValidate',
            'socket_id','profile',
            'created_at'
        ]

class CompanyStaffDetailsSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(source='user.username',read_only=True)
    department_name = serializers.SerializerMethodField(read_only=True)
    possition_name = serializers.SerializerMethodField(read_only=True)
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    def get_possition_name(self, obj):
        return obj.possition.name if obj.possition else None
    def get_profile(self, qs):
        try:
            profile=company_staff_profile.objects.get(staff=qs)
            return CompanyStaffProfileSerializer(profile).data
        except company_staff_profile.DoesNotExist:
            return None
            
    class Meta:
        model = company_staff
        fields = [
            'id','name','username',
            'company','user','department',
            'possition','isSuperAdmin','isActive','isAdmin',
            'isOnline','isValidate','socket_id','profile',
            'created_at','department_name','possition_name'
        ]

class CompanyStaffFullnameSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField(read_only=True)
    def get_fullname(self, qs):
        try:
            profile=company_staff_profile.objects.get(staff=qs)
            return profile.full_name
        except company_staff_profile.DoesNotExist:
            return None
    class Meta:
        model = company_staff
        fields = ['id','name','fullname','created_at']

class company_staffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = company_staff
        fields = ['company','name','username','department','possition','isSuperAdmin',
                  'isAdmin','isOnline','isValidate','socket_id','created_at']

class company_staffFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_staff
        fields = '__all__'

class company_staff_profileSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source='avatar.data', allow_null=True,read_only=True)
    background = serializers.CharField(source='background.data', allow_null=True,read_only=True)
    class Meta:
        model = company_staff_profile
        fields = '__all__'

class company_departmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_department
        fields = '__all__'

class company_possitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_possition
        fields = '__all__'

class CD_LTESerializer(serializers.ModelSerializer):
    class Meta:
        model = company_department
        fields = '__all__'

class CP_LTESerializer(serializers.ModelSerializer):
    class Meta:
        model = company_possition
        fields = '__all__'

class CompanyAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = company_account
        fields = ['username', 'password']
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = make_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
class CompanyAccountDetailsSerializer(serializers.ModelSerializer):
    user = CompanyAccountSerializer(write_only=True)
    username=serializers.SerializerMethodField(read_only=True)
    department_name = serializers.SerializerMethodField(read_only=True)
    possition_name = serializers.SerializerMethodField(read_only=True)
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    def get_possition_name(self, obj):
        return obj.possition.name if obj.possition else None
    def get_username(self, obj):
        return obj.user.username if obj.user else None
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)  # Lấy thông tin user nếu có
        company_account_instance = instance.user
        if user_data:
            username = user_data.get('username')
            password = user_data.get('password')
            if company_account_instance:
                if username:
                    company_account_instance.username = username
                if password:
                    company_account_instance.password = password
                company_account_instance.save()
            else:
                company_account_instance = company_account.objects.create(
                    user=instance.user,
                    company=instance.company,
                    username=username,
                    password=password
                )
                instance.user = company_account_instance
        return super().update(instance, validated_data)
    class Meta:
        model = company_staff
        fields = '__all__'
       
class OperatorHistorySerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField(read_only=True)
    supplier = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = operator_history
        fields = '__all__'
    def get_vendor(self, qs):
        if qs.vendor:
            return CompanyCustomerLTESerializer(qs.vendor,many=False).data
    def get_customer(self, qs):
        if qs.customer:
            return CompanyCustomerLTESerializer(qs.customer,many=False).data
    def get_supplier(self, qs):
        if qs.supplier:
            return CompanyCustomerLTESerializer(qs.supplier,many=False).data
            
class CompanyOperatorSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = company_operator
        fields = '__all__'
            
class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_operator
        fields = ['ho_ten','trangthai']
            
class OP_HISTSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField(read_only=True)
    supplier = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = operator_history
        fields = '__all__'
    def get_vendor(self, qs):
        if qs.vendor:
            return {
                "name":qs.vendor.name,
                "fullname": qs.vendor.fullname,
            }
    def get_customer(self, qs):
        if qs.customer:
            return {
                "name":qs.customer.name,
                "fullname": qs.customer.fullname,
            }
    def get_supplier(self, qs):
        if qs.supplier:
            return {
                "name":qs.supplier.name,
                "fullname": qs.supplier.fullname,
            }
         
class CompanyOperatorDetailsSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    work = serializers.SerializerMethodField(read_only=True)
    nguoituyen = serializers.SerializerMethodField(read_only=True)
    nguoibaocao = serializers.SerializerMethodField(read_only=True)
    congty_danglam = serializers.SerializerMethodField(read_only=True)
    nhachinh = serializers.SerializerMethodField(read_only=True)
    nhacungcap = serializers.SerializerMethodField(read_only=True)
    thamnien = serializers.SerializerMethodField(read_only=True)
    def get_thamnien(self, obj):
        def calculate_seniority(record):
            if not record.start_date:
                return 0
            start_date = record.start_date.date()
            end_date = (record.end_date or datetime.now()).date()
            delta_days = (end_date - start_date).days + 1
            if record.noihopdong:
                delta_days += calculate_seniority(record.noihopdong)
            return delta_days
        qs_history=operator_history.objects.filter(operator=obj).first()
        if qs_history:
            total_days = calculate_seniority(qs_history)
            return total_days
        else:
            return None
    
    def get_congty_danglam(self, qs):
        if qs.congty_danglam:
            return {
                "name":qs.congty_danglam.name,
                "fullname":qs.congty_danglam.fullname,
            }
    def get_nhacungcap(self, qs):
        if qs.nhacungcap:
            return {
                "name":qs.nhacungcap.name,
                "fullname":qs.nhacungcap.fullname,
            }
    def get_nhachinh(self, qs):
        if qs.nhachinh:
            return {
                "name":qs.nhachinh.name,
                "fullname":qs.nhachinh.fullname,
            }
    def get_nguoibaocao(self, qs):
        try:
            if qs.nguoibaocao:
                qs_profile=company_staff_profile.objects.filter(staff=qs.nguoibaocao)
                return {
                    "id":qs.nguoibaocao.id,
                    "name":qs.nguoibaocao.name,
                    "full_name":qs_profile.first().full_name if len(qs_profile)>0 else None
                }
        except Exception as e:
            return None
    def get_nguoituyen(self, qs):
        try:
            if qs.nguoituyen:
                qs_profile=company_staff_profile.objects.filter(staff=qs.nguoituyen)
                return {
                    "id":qs.nguoituyen.id,
                    "name":qs.nguoituyen.name,
                    "full_name":qs_profile.first().full_name if len(qs_profile)>0 else None
                }
        except Exception as e:
            return None
    def get_work(self, qs):
        qs_work=operator_history.objects.filter(operator=qs)
        if len(qs_work)>0:
            return [OP_HISTSerializer(qs_work.first()).data]
        else:
            return []
    class Meta:
        model = company_operator
        fields = '__all__'
           
class CompanyStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_staff
        fields = ['id', 'name', 'department', 'possition']  # Chỉ các trường cần thiết

class CompanySupplierSerializer(serializers.ModelSerializer):
    staffs = CompanyStaffSerializer(many=True, read_only=True)  # Dùng serializer lồng ghép để hiển thị nhân viên
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = company_supplier
        fields = ['id','company','staffs','name', 'fullname','website', 'address', 'email', 'hotline', 'created_at', 'updated_at']

class CompanyCustomerSerializer(serializers.ModelSerializer):
    staffs = CompanyStaffSerializer(many=True, read_only=True)  # Dùng serializer lồng ghép để hiển thị nhân viên
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = company_customer
        fields = ['id','company','staffs','name', 'fullname','website', 'address', 'email', 'hotline', 'created_at', 'updated_at']

class CompanyVendorSerializer(serializers.ModelSerializer):
    staffs = CompanyStaffSerializer(many=True, read_only=True)  # Dùng serializer lồng ghép để hiển thị nhân viên
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = company_vendor
        fields = ['id','company','staffs','name', 'fullname','website', 'address', 'email', 'hotline', 'created_at', 'updated_at']

class CompanyCustomerLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = company_customer
        fields = ['id','name','fullname','website', 'address', 'email', 'hotline', 'created_at' ]

class CompanySupplierLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = company_supplier
        fields = ['id','name','fullname','website', 'address', 'email', 'hotline', 'created_at' ]
class CompanyVendorLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = company_vendor
        fields = ['id','name','fullname','website', 'address', 'email', 'hotline', 'created_at' ]
class companyDetailsSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source='avatar.data', allow_null=True,read_only=True)
    wallpaper = serializers.CharField(source='wallpaper.data', allow_null=True,read_only=True)
    companyType = serializers.CharField(source='companyType.name', allow_null=True,read_only=True)
    department = serializers.SerializerMethodField(read_only=True)
    jobtitle = serializers.SerializerMethodField(read_only=True)
    custommer = serializers.SerializerMethodField(read_only=True)
    supplier = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    def get_department(self, qs):
        qs_department=company_department.objects.filter(company=qs)
        return CD_LTESerializer(qs_department,many=True).data
    def get_jobtitle(self, qs):
        qs_possition=company_possition.objects.filter(company=qs)
        return CP_LTESerializer(qs_possition,many=True).data
    def get_custommer(self, qs):
        qs_customer=company_customer.objects.filter(company=qs)
        return {
            "count": len(qs_customer),
            "data" : CompanyCustomerLTESerializer(qs_customer[:5],many=True).data
        }
    def get_supplier(self, qs):
        qs_supplier=company_supplier.objects.filter(company=qs)
        return {
            "count": len(qs_supplier),
            "data" : CompanyCustomerLTESerializer(qs_supplier[:5],many=True).data
        }
    def get_vendor(self, qs):
        qs_vendor=company_vendor.objects.filter(company=qs)
        return {
            "count": len(qs_vendor),
            "data" : CompanyCustomerLTESerializer(qs_vendor[:5],many=True).data
        }
            
    class Meta:
        model = company
        fields = ['id','companyType','avatar','name','fullname','address','department','wallpaper',
        'addressDetails','hotline','isValidate','isOA','jobtitle','custommer','taxCode',
        'supplier','vendor','shortDescription','description','created_at',
        'zalo','website','instagram','tiktok','facebook']

class companySublistSerializer(serializers.ModelSerializer):
    custommer = serializers.SerializerMethodField(read_only=True)
    supplier = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    staff = serializers.SerializerMethodField(read_only=True)
    def get_staff(self, qs):
        qs_staff=company_staff.objects.filter(company=qs)
        return {
            "count": len(qs_staff),
            "data" : CompanyStaffFullnameSerializer(qs_staff,many=True).data
        }
    def get_custommer(self, qs):
        qs_customer=company_customer.objects.filter(company=qs)
        return {
            "count": len(qs_customer),
            "data" : CompanyCustomerLTESerializer(qs_customer,many=True).data
        }
    def get_supplier(self, qs):
        qs_supplier=company_supplier.objects.filter(company=qs)
        return {
            "count": len(qs_supplier),
            "data" : CompanySupplierLTESerializer(qs_supplier,many=True).data
        }
    def get_vendor(self, qs):
        qs_vendor=company_vendor.objects.filter(company=qs)
        return {
            "count": len(qs_vendor),
            "data" : CompanyVendorLTESerializer(qs_vendor,many=True).data
        }
            
    class Meta:
        model = company
        fields = ['id','companyType','custommer','staff',
        'supplier','vendor','created_at']
        
    
class AdvanceTypeSerializer(serializers.ModelSerializer):     
    class Meta:
        model = AdvanceType
        fields = '__all__'
class AdvanceReasonTypeSerializer(serializers.ModelSerializer):     
    class Meta:
        model = AdvanceReasonType
        fields = '__all__'
        
class AdvanceRequestHistorySerializer(serializers.ModelSerializer):
    user = CompanyStaffDetailsSerializer(allow_null=True)  
    class Meta:
        model = AdvanceRequestHistory
        fields = '__all__'
        
class AdvanceRequestSerializer(serializers.ModelSerializer):
    reason = AdvanceReasonTypeSerializer(allow_null=True)
    requesttype = AdvanceTypeSerializer()
    requester = CompanyStaffSmallSerializer(allow_null=True)
    operator = OperatorSerializer(allow_null=True)
    history = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    retrieve_status_display = serializers.CharField(source='get_retrieve_status_display', read_only=True)
    hinhthucThanhtoan_display = serializers.CharField(source='get_hinhthucThanhtoan_display', read_only=True)
    nguoiThuhuong_display = serializers.CharField(source='get_nguoiThuhuong_display', read_only=True)
    def get_history(self, qs):
        qs_his=AdvanceRequestHistory.objects.filter(request=qs)
        return AdvanceRequestHistorySerializer(qs_his,many=True).data
    class Meta:
        model = AdvanceRequest
        fields = '__all__'
              
class AdvanceRequestDetailsSerializer(serializers.ModelSerializer):
    reason = AdvanceReasonTypeSerializer(allow_null=True)
    requesttype = AdvanceTypeSerializer()
    approver = CompanyStaffDetailsSerializer(allow_null=True)
    requester = CompanyStaffDetailsSerializer(allow_null=True)
    operator = CompanyOperatorDetailsSerializer(allow_null=True)
    history = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    retrieve_status_display = serializers.CharField(source='get_retrieve_status_display', read_only=True)
    hinhthucThanhtoan_display = serializers.CharField(source='get_hinhthucThanhtoan_display', read_only=True)
    nguoiThuhuong_display = serializers.CharField(source='get_nguoiThuhuong_display', read_only=True)
    def get_history(self, qs):
        qs_his=AdvanceRequestHistory.objects.filter(request=qs)
        return AdvanceRequestHistorySerializer(qs_his,many=True).data
    class Meta:
        model = AdvanceRequest
        fields = '__all__'
         
class CompanyOperatorMoreDetailsSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    work = serializers.SerializerMethodField(read_only=True)
    nguoituyen = serializers.SerializerMethodField(read_only=True)
    nguoibaocao = serializers.SerializerMethodField(read_only=True)
    congty_danglam = serializers.SerializerMethodField(read_only=True)
    nhachinh = serializers.SerializerMethodField(read_only=True)
    nhacungcap = serializers.SerializerMethodField(read_only=True)
    thamnien = serializers.SerializerMethodField(read_only=True)
    baoung = serializers.SerializerMethodField(read_only=True)
    def get_baoung(self, qs):
        try:
            qs_baoung=AdvanceRequest.objects.filter(operator=qs)
            return AdvanceRequestSerializer(qs_baoung,many=True).data
        except Exception as e:
            return None
    def get_thamnien(self, qs):
        return None
    def get_congty_danglam(self, qs):
        if qs.congty_danglam:
            return {
                "name":qs.congty_danglam.name,
                "fullname":qs.congty_danglam.fullname,
            }
    def get_nhacungcap(self, qs):
        if qs.nhacungcap:
            return {
                "name":qs.nhacungcap.name,
                "fullname":qs.nhacungcap.fullname,
            }
    def get_nhachinh(self, qs):
        if qs.nhachinh:
            return {
                "name":qs.nhachinh.name,
                "fullname":qs.nhachinh.fullname,
            }
    def get_nguoibaocao(self, qs):
        try:
            if qs.nguoibaocao:
                qs_profile=company_staff_profile.objects.filter(staff=qs.nguoibaocao)
                return {
                    "id":qs.nguoibaocao.id,
                    "name":qs.nguoibaocao.name,
                    "full_name":qs_profile.first().full_name if len(qs_profile)>0 else None
                }
        except Exception as e:
            return None
    def get_nguoituyen(self, qs):
        try:
            if qs.nguoituyen:
                qs_profile=company_staff_profile.objects.filter(staff=qs.nguoituyen)
                return {
                    "id":qs.nguoituyen.id,
                    "name":qs.nguoituyen.name,
                    "full_name":qs_profile.first().full_name if len(qs_profile)>0 else None
                }
        except Exception as e:
            return None
    def get_work(self, qs):
        qs_work=operator_history.objects.filter(operator=qs)
        return OP_HISTSerializer(qs_work,many=True).data
    class Meta:
        model = company_operator
        fields = '__all__'
   