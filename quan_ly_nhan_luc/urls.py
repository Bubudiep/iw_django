from django.urls import path, include
from rest_framework import routers
from . import api
router = routers.DefaultRouter()
router.register(r'employee', api.CompanyStaffViewSet, basename='employee')
urlpatterns = [
    path('login/', api.LoginOAuth2APIView.as_view(), name='login'),
    path('congty/', api.GetCompanyAPIView.as_view(), name='congty'),
    path('user/', api.GetUserAPIView.as_view(), name='user'),
    path('', include(router.urls)),
]