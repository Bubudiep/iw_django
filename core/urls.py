from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('att/', include('attendance.urls')),
    path('nl-api/', include('quan_ly_nhan_luc.urls')),
    path('api/', include('app.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('', admin.site.urls),
    path('admin/', admin.site.urls),
]