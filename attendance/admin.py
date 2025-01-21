from django.contrib import admin
from .models import *

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'company', 'created_at', 'updated_at')
    search_fields = ('username', 'company__name')
    list_filter = ('company',)
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'deparment', 'created_at')
    search_fields = ('user__username', 'full_name')
    
@admin.register(Punchtime)
class PunchtimeAdmin(admin.ModelAdmin):
    list_display = ('user', 'punch_time', 'att_date')
    search_fields = ('user__username',)
    
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'emp_id', 'att_date', 'clock_in', 'clock_out', 'is_check')
    search_fields = ('emp_id','att_date',)
    readonly_fields = ('punch_time',)
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return self.readonly_fields
    
@admin.register(AttendanceTicket)
class AttendanceTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'implement', 'attendance', 'is_check', 'is_close')
    search_fields = ('user__username', 'attendance__att_date')
    
@admin.register(AttendanceTicketComment)
class AttendanceTicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'comment', 'created_at')
    search_fields = ('ticket__user__username', 'comment')

@admin.register(EmployeeMessage)
class EmployeeMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'implement', 'title', 'is_check', 'is_close')
    search_fields = ('user__username', 'title')

@admin.register(EmployeeMessageComment)
class EmployeeMessageCommentAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'comment', 'created_at')
    search_fields = ('message__user__username', 'comment')