from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/', include('app.urls')),  # Thay 'myapp' bằng tên ứng dụng của bạn
]