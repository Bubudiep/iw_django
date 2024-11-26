from django.contrib import admin
from .models import *

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('name', 'user', 'created_at')
    search_fields = ('user',)
    list_filter = ('user',)

@admin.register(Photos)
class PhotosAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('filename', 'is_active', 'user', 'created_at')
    search_fields = ('filename',)
    list_filter = ('is_active',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('user', 'full_name', 'zalo_name', 'address', 'created_at', 'updated_at')
    search_fields = ('full_name', 'zalo_name')
    list_filter = ('created_at', 'tinh')
    
@admin.register(Tuchamcong)
class TuchamcongAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tencongty', 'user', 'bophan', 'chucvu', 'is_active', 'created_at', 'updated_at')
    search_fields = ('tencongty', 'user__username', 'bophan', 'chucvu')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)

@admin.register(Tutinhluong)
class TutinhluongAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tenluong', 'tuchamcong', 'tinhvaotangca', 'created_at')
    search_fields = ('tenluong', 'tuchamcong__tencongty')
    list_filter = ('tinhvaotangca', 'created_at')
    ordering = ('-created_at',)

@admin.register(TutinhChuyencan)
class TutinhChuyencanAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tuchamcong', 'socongyeucau', 'tienchuyencan', 'created_at')
    search_fields = ('tuchamcong__tencongty',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Tuchamcongtay)
class TuchamcongtayAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tuchamcong', 'ngay', 'giovao', 'giora', 'created_at')
    search_fields = ('tuchamcong__tencongty',)
    list_filter = ('ngay', 'created_at')
    ordering = ('-ngay',)

@admin.register(Kieungay)
class KieungayAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tuchamcong', 'tenloaingay', 'ngaycuthe', 'ngaytrongtuan', 'created_at')
    search_fields = ('tuchamcong__tencongty', 'tenloaingay')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Kieuca)
class KieucaAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tuchamcong', 'tenca', 'created_at')
    search_fields = ('tuchamcong__tencongty', 'tenca')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Heso)
class HesoAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('tuchamcong', 'kieungay', 'kieuca', 'batdau', 'ketthuc', 'heso', 'created_at')
    search_fields = ('tuchamcong__tencongty', 'kieungay__tenloaingay', 'kieuca__tenca')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Fixed_link)
class Fixed_linkAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Nhatro)
class NhatroAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Phong)
class PhongAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Nguoitro)
class NguoitroAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
   
@admin.register(LichsuNguoitro)
class LichsuNguoitroAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
  
# Tạo một InlineAdmin để hiển thị ChiTietThanhToan
class DanhsachAdminAdminInline(admin.TabularInline):  # Hoặc bạn có thể dùng StackedInline
    model = DanhsachAdmin
    extra = 1  # Số lượng bản ghi ChiTietThanhToan mặc định
    list_display = ('congty', 'zalo_id', 'isAdmin', 'isStaff', 'ghichu')
@admin.register(DanhsachCongty)
class DanhsachCongtyAdmin(admin.ModelAdmin):
    inlines = [DanhsachAdminAdminInline]
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(DanhsachAdmin)
class DanhsachAdminAdmin(admin.ModelAdmin):
    list_display = ('congty', 'zalo_id', 'isAdmin', 'isStaff', 'ghichu')
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(DanhsachNhanvien)
class DanhsachNhanvienAdmin(admin.ModelAdmin):
    list_display = ('congty', 'manhanvien', 'HovaTen', 'nguoituyen', 'created_at')
    search_fields = ('congty__tencongty', 'manhanvien')
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(DanhsachNhanvien_record)
class DanhsachNhanvien_recordAdmin(admin.ModelAdmin):
    search_fields = ('nhanvien__congty__tencongty', 'nhanvien__manhanvien')
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(DanhsachnhanvienDilam)
class DanhsachnhanvienDilamAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
# Tạo một InlineAdmin để hiển thị ChiTietThanhToan
class ChiTietThanhToanInline(admin.TabularInline):  # Hoặc bạn có thể dùng StackedInline
    model = ChiTietThanhToan
    extra = 1  # Số lượng bản ghi ChiTietThanhToan mặc định
    readonly_fields = ['so_tien', 'ghichu', 'created_at', 'updated_at']

@admin.register(LichsuThanhToan)
class LichsuThanhToanAdmin(admin.ModelAdmin):
    inlines = [ChiTietThanhToanInline]
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
class Restaurant_staffInline(admin.TabularInline):  # Hoặc bạn có thể dùng StackedInline
    model = Restaurant_staff
    extra = 0
    fields = ["user","is_Admin","is_Active"]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [Restaurant_staffInline]
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
@admin.register(UserLikeLog)
class UserLikeLogAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Restaurant_menu_items)
class Restaurant_menu_itemsAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ("name",
        "price",
        "is_hot",
        "is_new",
        "is_online",
        "is_ship",
        "is_available",
        "is_active",
        "is_delete",
        "is_validate")
    list_editable=(
        "is_ship",
        "is_available",
        "is_active",
        "is_delete",
        "is_validate")
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_menu_groups)
class Restaurant_menu_groupsAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_socket)
class Restaurant_socketAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_order)
class Restaurant_orderAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_space_group)
class Restaurant_space_groupAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_layout)
class Restaurant_layoutAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_staff)
class Restaurant_staffAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(Restaurant_space)
class Restaurant_spaceAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display_links = ("name",) 
    list_editable=(
        "is_inuse",
        "is_active",
        "is_ordering",)
    list_display = ("name",
        "group",
        "user_use",
        "is_inuse",
        "is_active",
        "is_ordering",
        "description",
        "created_at",
        "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ('created_at',)
    ordering = ('-created_at',)