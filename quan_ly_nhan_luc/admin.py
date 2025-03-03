from django.contrib import admin
from .models import *


@admin.register(image_safe)
class image_safeAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('name', 'user', 'created_at')
    search_fields = ('user',)
    list_filter = ('user',)

@admin.register(company_type)
class company_typeAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('name', 'created_at')
    search_fields = ()
    list_filter = ()

@admin.register(company)
class companyAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('name','companyType','isActive',
      'isValidate','isOA', 'created_at')
    search_fields = ('name', 'companyCode')
    list_filter = ()

@admin.register(company_account)
class company_accountAdmin(admin.ModelAdmin):
    list_display = ('username','password','updated_at','created_at')
    save_as = True  # Kích hoạt Save as new
    search_fields = ()
    list_filter = ()
    
@admin.register(company_department)
class company_departmentAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('name','isActive','description','created_at')
    search_fields = ('name', 'company__name')
    list_filter = ()

@admin.register(company_possition)
class company_possitionAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('id', 'name', 'company', 'department', 'isActive')
    search_fields = ('name', 'company__name', 'department__name')
    
class IsActiveAndNotBannedFilter(admin.SimpleListFilter):
    title = 'Active and Not Banned'  # Tên hiển thị trong bộ lọc
    parameter_name = 'active_not_banned'  # Query param trên URL
    def lookups(self, request, model_admin):
        return [
            ('yes', 'Active and Not Banned'),
            ('no', 'Inactive or Banned'),
        ]
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(isActive=True, isBan=False)
        if self.value() == 'no':
            return queryset.exclude(isActive=True, isBan=False)

    
@admin.register(operator_history)
class operator_historyAdmin(admin.ModelAdmin):
    list_display = ['operator', 'customer', 'vendor', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date', 'vendor', 'customer']
    search_fields = ['operator__ma_nhanvien', 'customer__name', 'vendor__name']
    
class CompanyStaffAdmin(admin.ModelAdmin):
    list_display = ['user','name', 'company', 'department', 'possition', 'isActive', 'isSuperAdmin', 'isAdmin', 'isBan', 'isOnline', 'isValidate']
    list_filter = ['isActive', 'isSuperAdmin', 'isAdmin', 'isBan', 'isOnline', 'isValidate', 'company', 'department', 'possition', IsActiveAndNotBannedFilter]
    search_fields = ['user__username', 'company__name', 'department__name', 'possition__name']
class CompanyStaffHistoryFunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )
class CompanyStaffHistoryActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )
class CompanyStaffHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'function', 'action', 'ip_action', 'created_at', 'isHidden', 'isSended', 'isReceived', 'isReaded')
    list_filter = ('function', 'action', 'isHidden', 'isSended', 'isReceived', 'isReaded')
    search_fields = ('staff__name', 'title', 'message', 'ip_action')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('staff', 'function', 'action', 'ip_action')
        }),
        ('Dữ liệu', {
            'fields': ('old_data', 'new_data')
        }),
        ('Thông tin thêm', {
            'fields': ('title', 'message', 'isHidden', 'isSended', 'isReceived', 'isReaded')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )
admin.site.register(company_staff, CompanyStaffAdmin)
admin.site.register(company_staff_history, CompanyStaffHistoryAdmin)
admin.site.register(company_staff_history_function, CompanyStaffHistoryFunctionAdmin)
admin.site.register(company_staff_history_action, CompanyStaffHistoryActionAdmin)

# Register company_customer with customization
@admin.register(company_customer)
class CompanyCustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'email', 'hotline', 'website', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'fullname', 'email', 'hotline', 'website')
    list_filter = ('company', 'created_at')
    ordering = ('-id',)
    readonly_fields = ('created_at', 'updated_at')

# Register company_supplier with customization
@admin.register(company_supplier)
class CompanySupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'email', 'hotline', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'fullname', 'email', 'hotline')
    list_filter = ('company', 'created_at')
    ordering = ('-id',)
    readonly_fields = ('created_at', 'updated_at')

# Register company_vendor with customization
@admin.register(company_vendor)
class CompanyVendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'email', 'hotline', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'fullname', 'email', 'hotline')
    list_filter = ('company', 'created_at')
    ordering = ('-id',)
    readonly_fields = ('created_at', 'updated_at')

# Register company_operator with customization
@admin.register(company_operator)
class CompanyOperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'ma_nhanvien', 'ho_ten', 'sdt', 'so_cccd', 'company', 'created_at', 'updated_at')
    search_fields = ('ma_nhanvien', 'ho_ten', 'sdt', 'so_cccd')
    list_filter = ('company', 'ngaysinh', 'created_at')
    ordering = ('-id',)
    readonly_fields = ('company','created_at', 'updated_at')
    fieldsets = (
        ("Company", {
            'fields': ('company',)
        }),
        ("Personal Details", {
            'fields': ('ma_nhanvien', 'ho_ten', 'sdt', 'so_cccd', 'ngaysinh', 'diachi')
        }),
        ("Account Details", {
            'fields': ('so_taikhoan', 'chu_taikhoan', 'ghichu_taikhoan')
        }),
        ("Company Relationships", {
            'fields': ('congty_danglam', 'nguoituyen', 'nhacungcap', 'nhachinh')
        }),
        ("Additional Info", {
            'fields': ('ghichu',)
        }),
    )
    
@admin.register(IntegrityErrorLog)
class IntegrityErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'models_name', 'api_name', 'error_message', 'timestamp', 'endpoint')  # Hiển thị các trường trong danh sách
    list_filter = ('models_name','api_name','timestamp', 'endpoint')  # Lọc theo thời gian hoặc endpoint
    search_fields = ('api_name','models_name','endpoint')  # Tìm kiếm theo thông báo lỗi hoặc endpoint
    ordering = ('-timestamp',)  # Sắp xếp theo thời gian (mới nhất trước)
    readonly_fields = ('api_name','models_name','error_message', 'timestamp', 'endpoint', 'payload')

@admin.register(company_staff_profile)
class CompanyStaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'staff', 'full_name', 'nick_name', 'phone', 
        'email', 'birthday', 'created_at', 'updated_at'
    )  # Các trường hiển thị trong danh sách
    list_filter = ('created_at', 'updated_at', 'birthday')  # Bộ lọc theo ngày/thời gian
    search_fields = ('full_name', 'nick_name', 'phone', 'email')  # Tìm kiếm theo tên, điện thoại, email
    ordering = ('-id',)  # Sắp xếp theo ID giảm dần
    readonly_fields = ('created_at', 'updated_at')  # Trường chỉ đọc

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('staff', 'last_name', 'first_name', 'full_name', 'nick_name', 'sologan')
        }),
        ('Thông tin liên hệ', {
            'fields': ('phone', 'email', 'zalo_id', 'zalo_number', 'facebook', 'tiktok', 'instagram')
        }),
        ('Thông tin ngân hàng', {
            'fields': ('bank', 'bank_number')
        }),
        ('Hình ảnh và tệp đính kèm', {
            'fields': ('avatar', 'background', 'cv_file')
        }),
        ('Thông tin khác', {
            'fields': ('birthday', 'created_at', 'updated_at')
        }),
    )  # Phân nhóm các trường trong form chi tiết

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'min_company_level', 'created_at', 'updated_at')
    list_filter = ('min_company_level', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

@admin.register(CompanyPermission)
class CompanyPermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'permission', 'is_active', 'assigned_by', 'assigned_at')
    list_filter = ('is_active', 'company', 'permission')
    search_fields = ('company__name', 'permission__name')
    ordering = ('-assigned_at',)
    autocomplete_fields = ('company', 'permission', 'assigned_by', 'applicable_staff', 'applicable_departments', 'applicable_positions', 'excluded_staff')
    filter_horizontal = ('applicable_staff', 'applicable_departments', 'applicable_positions', 'excluded_staff')

class AdvanceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'typecode', 'need_operator', 'need_approver', 'company', 'created_at', 'updated_at')
    search_fields = ('typecode', 'company__name')  # You can customize this as needed
    list_filter = ('need_operator', 'need_approver', 'company')
    ordering = ['-created_at']

# Admin for AdvanceReasonType model
class AdvanceReasonTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'typename', 'company', 'created_at', 'updated_at')
    search_fields = ('typename', 'company__name')  # You can customize this as needed
    list_filter = ('company',)
    ordering = ['-created_at']
    
class AdvanceRequestHistoryInline(admin.TabularInline):  
    model = AdvanceRequestHistory  
    extra = 0  # Không hiển thị dòng trống
    readonly_fields = ('user', 'action', 'old_data', 'new_data', 'comment', 'created_at')  
    can_delete = False  # Không cho phép xóa lịch sử
    
# Admin for AdvanceRequest model
class AdvanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'requesttype', 'approver', 'operator', 'amount', 'status', 'payment_status', 'retrieve_status', 'created_at')
    search_fields = ('requester__name', 'approver__name', 'operator__name', 'requesttype__typecode', 'amount')
    list_filter = ('status', 'payment_status', 'retrieve_status', 'company')
    ordering = ['-created_at']
    list_select_related = ('requester', 'approver', 'operator', 'requesttype', 'reason')  # Optimizes queries
    actions = ['mark_as_approved', 'mark_as_rejected']
    inlines = [AdvanceRequestHistoryInline] # Add the inline to the form
    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved')
    mark_as_approved.short_description = 'Mark selected requests as approved'
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = 'Mark selected requests as rejected'

# Register the models and their custom admin views
admin.site.register(AdvanceType, AdvanceTypeAdmin)
admin.site.register(AdvanceReasonType, AdvanceReasonTypeAdmin)
admin.site.register(AdvanceRequest, AdvanceRequestAdmin)