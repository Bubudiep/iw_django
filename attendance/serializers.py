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
from django.db import IntegrityError
from datetime import datetime
import pytz

def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class PunchtimeLTESerializer(serializers.ModelSerializer):
    class Meta:
        model = Punchtime
        fields = ["punch_time"]
        
class UserAttendanceSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', allow_null=True,read_only=True)
    punch_time = PunchtimeLTESerializer(many=True, read_only=True)
    class Meta:
        model = Attendance
        fields = "__all__"
        
class PunchtimeSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', allow_null=True,read_only=True)
    class Meta:
        model = Punchtime
        fields = "__all__"
        
class AttendanceDetailsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', allow_null=True,read_only=True)
    punch_time = PunchtimeSerializer(many=True, read_only=True)
    class Meta:
        model = Attendance
        fields = "__all__"
        
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', allow_null=True,read_only=True)
    class Meta:
        model = Profile
        fields = "__all__"

class PunchtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Punchtime
        fields = ['user', 'punch_time', 'att_date']

class AttendanceSerializer(serializers.ModelSerializer):
    punch_time = PunchtimeSerializer(many=True)

    class Meta:
        model = Attendance
        fields = ['user', 'week', 'weekday', 'clock_in', 'clock_out', 'punch_time', 'att_date', 'is_check']

    def create(self, validated_data):
        punch_time_data = validated_data.pop('punch_time')
        attendance = Attendance.objects.create(**validated_data)
        for punch_data in punch_time_data:
            punchtime = Punchtime.objects.create(**punch_data)
            attendance.punch_time.add(punchtime)
        return attendance