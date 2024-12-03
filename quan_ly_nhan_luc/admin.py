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
@admin.register(company_staff)
class company_staffAdmin(admin.ModelAdmin):
    save_as = True  # Kích hoạt Save as new
    list_display = ('company','user','department',
      'possition','isActive',
        'isSuperAdmin',
        'isAdmin',
        'isBan',
        'isOnline',
        'isValidate', 'created_at')
    search_fields = ()
    list_filter = ()
