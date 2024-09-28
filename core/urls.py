from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('app.urls')),  # Thay 'myapp' bằng tên ứng dụng của bạn
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('', admin.site.urls),
    path('admin/', admin.site.urls),
]