from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from datetime import time
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class file_safe(models.Model): # Phân loại công ty
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    data = models.FileField(null=True, blank=True)
    size = models.TextField(null=True, blank=True)
    fileType = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
class image_safe(models.Model): # Phân loại công ty
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    size = models.TextField(null=True, blank=True)
    width = models.TextField(null=True, blank=True)
    height = models.TextField(null=True, blank=True)
    fileType = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company_type(models.Model): # Phân loại công ty
    code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # người sở hữu
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # người sở hữu
    companyType = models.ForeignKey(company_type, on_delete=models.SET_NULL, null=True, blank=True)
    avatar= models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True)
    key = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.TextField(null=True, blank=True)
    companyCode = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    addressDetails = models.JSONField(null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    isValidate = models.BooleanField(default=False, null=True, blank=True)
    isOA = models.BooleanField(default=False, null=True, blank=True)
    shortDescription = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = uuid.uuid4().hex.upper()
        super(company, self).save(*args, **kwargs)
        
class company_department(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"    
      
class company_possition(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    department = models.ForeignKey(company_department, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"   
     
class company_account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(company, on_delete=models.CASCADE, related_name='employee_accounts')
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('company', 'username')  # Đảm bảo username duy nhất trong từng công ty
    def save(self, *args, **kwargs):
        if not self.username or not self.password:
            raise ValidationError("Username và password không được để trống.")
        if not self.password.startswith('pbkdf2_sha256$'):  # Kiểm tra xem mật khẩu đã mã hóa chưa
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} ({self.company.name})"
    
class company_staff(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True) # mã NV
    user = models.ForeignKey(company_account, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(company_department, on_delete=models.SET_NULL, null=True, blank=True) # bộ phận
    possition = models.ForeignKey(company_possition, on_delete=models.SET_NULL, null=True, blank=True) # vị trí
    isActive = models.BooleanField(default=False, null=True, blank=True) # nghỉ việc
    isSuperAdmin = models.BooleanField(default=False, null=True, blank=True)
    isAdmin = models.BooleanField(default=False, null=True, blank=True)
    isBan = models.BooleanField(default=False, null=True, blank=True) # bị ban
    isOnline = models.BooleanField(default=False, null=True, blank=True) # online trên app
    isValidate = models.BooleanField(default=False, null=True, blank=True) # được phê duyệt
    socket_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}_{self.user.username}_{self.possition}_{self.company}"
    
class company_staff_profile(models.Model):
    staff = models.ForeignKey(company_staff, on_delete=models.SET_NULL, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    nick_name = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True, related_name='avatar_img')
    background = models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True, related_name='background_img')
    cv_file = models.ForeignKey(file_safe, on_delete=models.SET_NULL, null=True, blank=True)
    isOnline = models.BooleanField(default=False, null=True, blank=True) # online trên app
    isValidate = models.BooleanField(default=False, null=True, blank=True) # được phê duyệt
    socket_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username}_{self.possition}_{self.company}"
    