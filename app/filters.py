import django_filters
from .models import *

class AlbumFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Photos
        fields = ['name']
       
class PhotosFilter(django_filters.FilterSet):
    filename = django_filters.CharFilter(lookup_expr='icontains')
    album = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Photos
        fields = ['filename', 'created_at', 'is_active', 'album']
        
class TuchamcongFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    tencongty = django_filters.CharFilter(lookup_expr='icontains')
    bophan = django_filters.CharFilter(lookup_expr='icontains')
    chucvu = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Tuchamcong
        fields = ['user', 'tencongty', 'bophan', 'chucvu', 'created_at', 'is_active']


class TutinhluongFilter(django_filters.FilterSet):
    tuchamcong = django_filters.ModelChoiceFilter(queryset=Tuchamcong.objects.all())
    tenluong = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Tutinhluong
        fields = ['tuchamcong', 'tenluong', 'created_at']


class TutinhChuyencanFilter(django_filters.FilterSet):
    tuchamcong = django_filters.ModelChoiceFilter(queryset=Tuchamcong.objects.all())
    socongyeucau = django_filters.RangeFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = TutinhChuyencan
        fields = ['tuchamcong', 'socongyeucau', 'created_at']


class TuchamcongtayFilter(django_filters.FilterSet):
    tuchamcong = django_filters.ModelChoiceFilter(queryset=Tuchamcong.objects.all())
    ngay = django_filters.DateFromToRangeFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Tuchamcongtay
        fields = ['tuchamcong', 'ngay', 'created_at']

class KieungayFilter(django_filters.FilterSet):
    tuchamcong = django_filters.ModelChoiceFilter(queryset=Tuchamcong.objects.all())
    tenloaingay = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Kieungay
        fields = ['tuchamcong', 'tenloaingay', 'created_at']


class KieucaFilter(django_filters.FilterSet):
    tuchamcong = django_filters.ModelChoiceFilter(queryset=Tuchamcong.objects.all())
    tenca = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Kieuca
        fields = ['tuchamcong', 'tenca', 'created_at']


class HesoFilter(django_filters.FilterSet):
    tuchamcong = django_filters.ModelChoiceFilter(queryset=Tuchamcong.objects.all())
    kieungay = django_filters.ModelChoiceFilter(queryset=Kieungay.objects.all())
    kieuca = django_filters.ModelChoiceFilter(queryset=Kieuca.objects.all())
    batdau = django_filters.TimeFilter()
    ketthuc = django_filters.TimeFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Heso
        fields = ['tuchamcong', 'kieungay', 'kieuca', 'batdau', 'ketthuc', 'created_at']


class CongtyFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Congty
        fields = ['created_at']

class TangFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Tang
        fields = ['created_at']

class LichsuNguoitroFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = LichsuNguoitro
        fields = ['created_at']

class LichsuTieuThuFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = LichsuTieuThu
        fields = ['created_at']

class NhatroFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    giaphongThapnhat = django_filters.RangeFilter()
    giaphongCaonhat = django_filters.RangeFilter()
    isActive = django_filters.BooleanFilter()

    class Meta:
        model = Nhatro
        fields = ['created_at', 'giaphongThapnhat', 'giaphongCaonhat', 'isActive']

class NguoitroFilter(django_filters.FilterSet):
    hoTen = django_filters.CharFilter(lookup_expr='icontains')
    sdt = django_filters.CharFilter(lookup_expr='icontains')
    cccd = django_filters.CharFilter(lookup_expr='icontains')
    isActive = django_filters.BooleanFilter()

    class Meta:
        model = Nguoitro
        fields = ['hoTen', 'sdt', 'cccd', 'isActive']

class PhongFilter(django_filters.FilterSet):
    giaPhong = django_filters.RangeFilter()
    soNguoiToida = django_filters.RangeFilter()

    class Meta:
        model = Phong
        fields = ['giaPhong', 'soNguoiToida']

class LichsuThanhToanFilter(django_filters.FilterSet):
    ngayThanhToan = django_filters.DateFromToRangeFilter()
    tongTien = django_filters.RangeFilter()

    class Meta:
        model = LichsuThanhToan
        fields = ['ngayThanhToan', 'tongTien']