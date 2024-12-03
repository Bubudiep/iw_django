from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db import transaction
from django.db.models import Max,Sum
from rest_framework.permissions import IsAuthenticated
from django.utils.functional import cached_property

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

class CompanyStaffDetailsSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)
    def get_profile(self, qs):
        try:
            profile=company_staff_profile.objects.get(staff=qs)
            return CompanyStaffProfileSerializer(profile).data
        except company_staff_profile.DoesNotExist:
            return None
            
    class Meta:
        model = company_staff
        fields = [
            'id','name',
            'company',
            'user',
            'department',
            'possition',
            'isSuperAdmin',
            'isActive',
            'isAdmin',
            'isOnline',
            'isValidate',
            'socket_id',
            'profile',
            'created_at'
        ]

class company_staffSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_staff
        fields = [
            'company',
            'user',
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

class company_departmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_department
        fields = '__all__'

class company_possitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_possition
        fields = '__all__'
