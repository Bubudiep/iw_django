from django.urls import path, include
from rest_framework import routers
from . import api

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet, basename='user_')
router.register(r'profiles', api.ProfileViewSet, basename='profile')
router.register(r'albums', api.AlbumViewSet, basename='albums')
router.register(r'photos', api.PhotosViewSet, basename='photos')
router.register(r'tuchamcong', api.TuchamcongViewSet, basename='tuchamcong')
router.register(r'tutinhluong', api.TutinhluongViewSet, basename='tutinhluong')
router.register(r'tutinhchuyencan', api.TutinhChuyencanViewSet, basename='tutinhchuyencan')
router.register(r'tuchamcongtay', api.TuchamcongtayViewSet, basename='tuchamcongtay')
router.register(r'kieungay', api.KieungayViewSet, basename='kieungay')
router.register(r'kieuca', api.KieucaViewSet, basename='kieuca')
router.register(r'heso', api.HesoViewSet, basename='heso')

urlpatterns = [
    path('zlogin/', api.ZaloLoginAPIView.as_view(), name='zalo_login'),
    path('login/', api.CustomTokenView.as_view(), name='login'),
    path('register/', api.RegisterView.as_view(), name='register'),
    path('', include(router.urls)),  # Thêm router vào urlpatterns
]
