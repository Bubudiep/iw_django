from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class RegisterSerializer(serializers.ModelSerializer):
    # Bạn có thể thêm các trường zalo_name và zalo_id vào đây
    zalo_name = serializers.CharField(required=False)
    zalo_id = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'email','zalo_name','zalo_id']

    def create(self, validated_data):
        # Lấy các thông tin zalo_name và zalo_id từ dữ liệu đã xác thực
        zalo_name = validated_data.pop('zalo_name', None)
        zalo_id = validated_data.pop('zalo_id',None)
        user = User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'],
                                        email=validated_data['email'])
        # create_profile
        if zalo_id is not None:
            qs_zalo_id=Profile.objects.filter(zalo_id=zalo_id).count()
            if qs_zalo_id==0:
                Profile.objects.create(
                    user=user,
                    zalo_name=zalo_name,
                    zalo_id=zalo_id
                )
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    def get_profile(self, user):
        try:
            qs_user=Profile.objects.get(user=user)
            print(f"Profile: {qs_user}")
            return ProfileSerializer(qs_user,many=False).data
        except:
            return []
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
class PhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = '__all__'

class WorkSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSheet
        fields = '__all__'

class WorkSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSalary
        fields = '__all__'

class WorkRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRecord
        fields = '__all__'