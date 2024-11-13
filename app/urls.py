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
router.register(r'noiquynhatro', api.NhatroNoiquyViewSet, basename='noiquynhatro')
router.register(r'congty', api.NhatroNoiquyViewSet, basename='congty')
router.register(r'phong', api.PhongViewSet, basename='phong')
router.register(r'thanhtoan', api.LichsuThanhToanViewSet, basename='thanhtoan')
router.register(r'nhatro', api.NhatroViewSet, basename='nhatro')
router.register(r'my_nhatro', api.DanhsachNhatroViewSet, basename='my_nhatro')
router.register(r'danhsachnhanvien', api.DanhsachNhanvienViewSet, basename='danhsachnhanvien')
router.register(r'danhsachdilam', api.DanhsachnhanvienDilamViewSet, basename='danhsachdilam')
router.register(r'dsdilam', api.DanhsachDilamViewSet, basename='dsdilam')
router.register(r'danhsachadmin', api.DanhsachAdminViewSet, basename='danhsachadmin')
router.register(r'res-items', api.Restaurant_menu_itemsViewSet, basename='res-items')

urlpatterns = [
    path('create-res/', api.CreateRestaurantAPIView.as_view(), name='create-res'),
    path('lenmon/', api.LenmonAppAPIView.as_view(), name='lenmon'),
    path('qr_login/', api.QR_loginAPIView.as_view(), name='qr_login'),
    path('kiemtra_tro/', api.KiemtraTroAPIView.as_view(), name='kiemtra_tro'),
    path('tamtru/', api.XacnhanTamtruAPIView.as_view(), name='tamtru'),
    path('them-nguoi/', api.ThemnguoivaoAPIView.as_view(), name='them-nguoi'),
    path('themtangtro/', api.ThemtangAPIView.as_view(), name='themtangtro'),
    path('tt-phong/', api.XacnhanThanhtoanAPIView.as_view(), name='tt-phong'),
    path('t-thanhtoan/', api.NhatroThanhtoanAPIView.as_view(), name='update_phong'),
    path('u-phong/', api.NhatroUpdateAPIView.as_view(), name='update_phong'),
    path('nha-tro/', api.NhaTroCreateView.as_view(), name='nha_tro_create'),
    path('zlogin/', api.ZaloLoginAPIView.as_view(), name='zalo_login'),
    path('login/', api.CustomTokenView.as_view(), name='login'),
    path('register/', api.RegisterView.as_view(), name='register'),
    path('dilam/', api.DilamAPIView.as_view(), name='dilam'),
    path('', include(router.urls)),  # Thêm router vào urlpatterns
]
