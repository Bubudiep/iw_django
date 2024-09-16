import django_filters
from .models import *

class PhotosFilter(django_filters.FilterSet):
    filename = django_filters.CharFilter(lookup_expr='icontains')
    album = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Photos
        fields = ['filename', 'created_at', 'is_active', 'album']

class WorkSheetFilter(django_filters.FilterSet):
    company = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = WorkSheet
        fields = ['company', 'created_at']