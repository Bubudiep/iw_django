from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()

class ZaloBackend(BaseBackend):
    def authenticate(self, request, zalo_id=None):
        try:
            return User.objects.get(profile__zalo_id=zalo_id)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
