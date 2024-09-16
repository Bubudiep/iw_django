import django_filters
from .models import Photos

class PhotosFilter(django_filters.FilterSet):
    filename = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Photos
        fields = ['filename', 'created_at', 'is_active', 'album']
