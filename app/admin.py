from django.contrib import admin
from .models import *

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('user',)
    list_filter = ('user',)

@admin.register(Photos)
class PhotosAdmin(admin.ModelAdmin):
    list_display = ('filename', 'is_active', 'user', 'created_at')
    search_fields = ('filename',)
    list_filter = ('is_active',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'zalo_name', 'address', 'created_at', 'updated_at')
    search_fields = ('full_name', 'zalo_name')
    list_filter = ('created_at', 'tinh')
    
@admin.register(Tuchamcong)
class TuchamcongAdmin(admin.ModelAdmin):
    list_display = ('tencongty', 'user', 'bophan', 'chucvu', 'is_active', 'created_at', 'updated_at')
    search_fields = ('tencongty', 'user__username', 'bophan', 'chucvu')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)

@admin.register(Tutinhluong)
class TutinhluongAdmin(admin.ModelAdmin):
    list_display = ('tenluong', 'tuchamcong', 'tinhvaotangca', 'created_at')
    search_fields = ('tenluong', 'tuchamcong__tencongty')
    list_filter = ('tinhvaotangca', 'created_at')
    ordering = ('-created_at',)

@admin.register(TutinhChuyencan)
class TutinhChuyencanAdmin(admin.ModelAdmin):
    list_display = ('tuchamcong', 'socongyeucau', 'tienchuyencan', 'created_at')
    search_fields = ('tuchamcong__tencongty',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Tuchamcongtay)
class TuchamcongtayAdmin(admin.ModelAdmin):
    list_display = ('tuchamcong', 'ngay', 'giovao', 'giora', 'created_at')
    search_fields = ('tuchamcong__tencongty',)
    list_filter = ('ngay', 'created_at')
    ordering = ('-ngay',)

@admin.register(Kieungay)
class KieungayAdmin(admin.ModelAdmin):
    list_display = ('tuchamcong', 'tenloaingay', 'ngaycuthe', 'ngaytrongtuan', 'created_at')
    search_fields = ('tuchamcong__tencongty', 'tenloaingay')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Kieuca)
class KieucaAdmin(admin.ModelAdmin):
    list_display = ('tuchamcong', 'tenca', 'created_at')
    search_fields = ('tuchamcong__tencongty', 'tenca')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Heso)
class HesoAdmin(admin.ModelAdmin):
    list_display = ('tuchamcong', 'kieungay', 'kieuca', 'batdau', 'ketthuc', 'heso', 'created_at')
    search_fields = ('tuchamcong__tencongty', 'kieungay__tenloaingay', 'kieuca__tenca')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Nhatro)
class NhatroAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(DanhsachCongty)
class DanhsachCongtyAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    ordering = ('-created_at',)
@admin.register(DanhsachAdmin)
class DanhsachAdminAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    ordering = ('-created_at',)
@admin.register(DanhsachNhanvien)
class DanhsachNhanvienAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    ordering = ('-created_at',)
@admin.register(DanhsachnhanvienDilam)
class DanhsachnhanvienDilamAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    ordering = ('-created_at',)