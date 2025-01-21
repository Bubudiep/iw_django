from django.urls import path, include
from rest_framework import routers
from . import views
router = routers.DefaultRouter()
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
urlpatterns = [
    path('add-attendance/', views.AttendanceAPIView.as_view(), name='attendance_api'),
    path('user/', views.UserView.as_view(), name='user'),
    path('last_punchtime/', views.LatestPunchtimeAPIView.as_view(), name='last_punchtime'),
    path('add-user/', views.RegisterView.as_view(), name='add-user'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]