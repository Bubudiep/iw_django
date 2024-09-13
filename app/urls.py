from django.urls import path, include
from rest_framework import routers
from . import api

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet, basename='user_')

urlpatterns = [
    path('login/', api.CustomTokenView.as_view(), name='login'),
    path('register/', api.RegisterView.as_view(), name='register'),
    path('', include(router.urls)),  # Thêm router vào urlpatterns
]
