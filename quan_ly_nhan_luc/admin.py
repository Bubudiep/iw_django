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

class CompanyStaffAdmin(admin.ModelAdmin):
    list_display = ['user','name', 'company', 'department', 'possition', 'isActive', 'isSuperAdmin', 'isAdmin', 'isBan', 'isOnline', 'isValidate']
    list_filter = ['isActive', 'isSuperAdmin', 'isAdmin', 'isBan', 'isOnline', 'isValidate', 'company', 'department', 'possition', IsActiveAndNotBannedFilter]
    search_fields = ['user__username', 'company__name', 'department__name', 'possition__name']

admin.site.register(company_staff, CompanyStaffAdmin)