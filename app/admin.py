from django.contrib import admin
from .models import *

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

@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_display = ("user",
                  "company",
                  "jobs_title",
                  "working_day",
                  "ngay_nghi",
                  "calamviec",
                  "finish_working_day",
                  "start_date",
                  "is_active",
                  "qr_code", 'created_at')
    search_fields = ('company', 'jobs_title')
    list_filter = ('is_active', 'created_at')

@admin.register(WorkSalary)
class WorkSalaryAdmin(admin.ModelAdmin):
    list_display = ("worksheet",
                  "salary_name",
                  "salary",
                  "is_monthly",
                  "is_tangca",
                  "checked_date",
                  "created_at")
    search_fields = ('salary_name',)
    list_filter = ('is_monthly', 'is_tangca')

@admin.register(WorkRecord)
class WorkRecordAdmin(admin.ModelAdmin):
    list_display = ('worksheet', 'leave_type', 'giobinhthuong', 'giotangca', 
                    'work_date', 'is_working', 'created_at')
    search_fields = ('work_sheet__Company',)
    list_filter = ('leave_type', 'is_working', 'created_at')
