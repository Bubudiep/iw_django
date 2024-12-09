from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db import transaction
from django.db.models import Max,Sum
from rest_framework.permissions import IsAuthenticated
from django.utils.functional import cached_property
import random
import string
import os
import sys
from rest_framework.response import Response
from rest_framework import status
def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}

class RegisterSerializer(serializers.ModelSerializer):
    # Bạn có thể thêm các trường zalo_name và zalo_id vào đây
    employeeCode = serializers.CharField(required=True)
    key = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    department = serializers.CharField(required=False)
    jobtitle = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'employeeCode','key','jobtitle','department']
        
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
                user = User.objects.create_user(username=f"EMP_{qs_company.id}_{username}",
                                                password=''.join(random.choices(string.ascii_letters 
                                                                        + string.digits, k=12)))
                emp = company_account.objects.create(company=qs_company,user=user,
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
        return emp
        
class companySerializer(serializers.ModelSerializer):
    class Meta:
        model = company
        fields = ['companyType','avatar','name','fullname','address',
        'addressDetails','hotline','isValidate','isOA',
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
            'created_at'
        ]

class company_staffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = company_staff
        fields = [
            'company',
            'name','username',
            'department',
            'possition',
            'isSuperAdmin',
            'isAdmin',
            'isOnline',
            'isValidate',
            'socket_id',
            'created_at'
        ]

class company_staffFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_staff
        fields = '__all__'

class company_staff_profileSerializer(serializers.ModelSerializer):
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

class companyDetailsSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField(read_only=True)
    jobtitle = serializers.SerializerMethodField(read_only=True)
    def get_department(self, qs):
        qs_department=company_department.objects.filter(company=qs)
        return CD_LTESerializer(qs_department,many=True).data
    def get_jobtitle(self, qs):
        qs_possition=company_possition.objects.filter(company=qs)
        return CP_LTESerializer(qs_possition,many=True).data
            
    class Meta:
        model = company
        fields = ['companyType','avatar','name','fullname','address','department',
        'addressDetails','hotline','isValidate','isOA','jobtitle',
        'shortDescription','description','created_at']
        
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
    class Meta:
        model = company_staff
        fields = '__all__'

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