from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    UserProfile = serializers.SerializerMethodField()
    def get_UserProfile(self, us):
        try:
            qs_user=UserProfile.objects.get(User=us)
            return UserProfileSerializer(qs_user,many=False).data
        except:
            return []
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }