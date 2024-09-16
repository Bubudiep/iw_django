from django.urls import path, include
from rest_framework import routers
from . import api

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet, basename='user_')
router.register(r'profiles', api.ProfileViewSet, basename='profile')
router.register(r'photos', api.PhotosViewSet, basename='photos')
router.register(r'worksheets', api.WorkSheetViewSet, basename='worksheet')
router.register(r'work_salaries', api.WorkSalaryViewSet, basename='work_salary')
router.register(r'work_records', api.WorkRecordViewSet, basename='work_record')

urlpatterns = [
    path('zlogin/', api.ZaloLoginAPIView.as_view(), name='zalo_login'),
    path('login/', api.CustomTokenView.as_view(), name='login'),
    path('register/', api.RegisterView.as_view(), name='register'),
    path('', include(router.urls)),  # Thêm router vào urlpatterns
]
