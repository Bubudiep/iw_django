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
class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    companyCode = django_filters.CharFilter(field_name='companyCode', lookup_expr='exact')
    isActive = django_filters.BooleanFilter(field_name='isActive')
    isValidate = django_filters.BooleanFilter(field_name='isValidate')
    companyType = django_filters.CharFilter(field_name='companyType__name', lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')
    class Meta:
        model = company
        fields = [
            'name', 'companyCode', 'isActive', 'isValidate', 'companyType', 'created_at'
        ]