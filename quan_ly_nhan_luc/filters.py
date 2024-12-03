import django_filters
from .models import *

class CompanyStaffFilter(django_filters.FilterSet):
    company = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')  # Lọc theo tên công ty
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')    # Lọc theo username
    isActive = django_filters.BooleanFilter(field_name='isActive')                            # Lọc theo trạng thái
    department = django_filters.CharFilter(field_name='department__name', lookup_expr='icontains')  # Bộ phận
    possition = django_filters.CharFilter(field_name='possition__name', lookup_expr='icontains')    # Vị trí
    class Meta:
        model = company_staff
        fields = ['company', 'user', 'isActive', 'department', 'possition', 'isBan', 'isAdmin', 'isSuperAdmin']