from .a import *
from .company import *
class Permission(models.Model):
    name = models.CharField(max_length=200)  # Tên quyền
    description = models.TextField(null=True, blank=True)  # Mô tả quyền
    min_company_level = models.PositiveIntegerField(default=1)  # Level tối thiểu của công ty để sử dụng quyền
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['-id']

    def __str__(self):
        return f"{self.name}"

class CompanyPermission(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # Quyền có đang được kích hoạt không
    assigned_by = models.ForeignKey(company_staff, on_delete=models.SET_NULL, null=True, blank=True)  # Ai cấp quyền
    assigned_at = models.DateTimeField(default=timezone.now)
    # Many-to-Many relationships
    applicable_staff = models.ManyToManyField(company_staff, related_name='company_permissions', blank=True)
    applicable_departments = models.ManyToManyField(company_department, related_name='company_permissions', blank=True)
    applicable_positions = models.ManyToManyField(company_possition, related_name='company_permissions', blank=True)
    # Excluded staff
    excluded_staff = models.ManyToManyField(company_staff, related_name='excluded_permissions', blank=True)
    class Meta:
        verbose_name = "Company Permission"
        verbose_name_plural = "Company Permissions"
        unique_together = ('company', 'permission')
    def __str__(self):
        return f"{self.company.name} - {self.permission.name}"
    