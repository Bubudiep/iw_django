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
    search_fields = ()
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
    search_fields = ()
    list_filter = ()

@admin.register(company_possition)
class company_possitionAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('name','isActive','description','created_at')
    search_fields = ()
    list_filter = ()
    
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