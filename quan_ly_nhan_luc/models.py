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
    cv_file = models.ForeignKey(file_safe, on_delete=models.SET_NULL, null=True, blank=True)
    
    avatar = models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True, related_name='avatar_img')
    background = models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True, related_name='background_img')
    
    full_name = models.CharField(max_length=200, null=True, blank=True)
    nick_name = models.CharField(max_length=200, null=True, blank=True)
    sologan = models.CharField(max_length=200, null=True, blank=True)

    bank = models.CharField(max_length=200, null=True, blank=True)
    bank_number = models.CharField(max_length=200, null=True, blank=True)
    
    zalo_id= models.CharField(max_length=200, null=True, blank=True)
    zalo_number = models.CharField(max_length=200, null=True, blank=True)
    facebook = models.CharField(max_length=200, null=True, blank=True)
    tiktok = models.CharField(max_length=200, null=True, blank=True)
    instagram = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username}_{self.possition}_{self.company}"

class company_staff_history_function(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company_staff_history_action(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company_staff_history(models.Model):
    staff = models.ForeignKey(company_staff, on_delete=models.SET_NULL, null=True, blank=True)

    function = models.ForeignKey(company_staff_history_function, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.ForeignKey(company_staff_history_action, on_delete=models.SET_NULL, null=True, blank=True)

    ip_action=models.GenericIPAddressField(null=True,blank=True)
    
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    
    title= models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    
    isHidden = models.BooleanField(default=False, null=True, blank=True)
    
    isSended = models.BooleanField(default=False, null=True, blank=True)
    isReceived = models.BooleanField(default=False, null=True, blank=True)
    isReaded = models.BooleanField(default=False, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.staff.name}"

class company_customer(models.Model):
    staffs = models.ManyToManyField(company_staff, related_name="customers", blank=True)
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company_supplier(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company_vendor(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class company_operator(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    ma_nhanvien= models.CharField(max_length=200, null=True, blank=True)
    
    sdt= models.CharField(max_length=15, null=True, blank=True)
    ho_ten= models.CharField(max_length=200, null=True, blank=True)
    ten_goc= models.CharField(max_length=200, null=True, blank=True)
    so_cccd= models.CharField(max_length=200, null=True, blank=True)
    diachi= models.CharField(max_length=200, null=True, blank=True)
    ngaysinh= models.DateField(null=True, blank=True)
    diachi= models.TextField(null=True, blank=True)
    
    so_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    chu_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    ghichu_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    ghichu= models.TextField(null=True, blank=True)
    
    nguoituyen = models.ForeignKey(company_staff, on_delete=models.SET_NULL, null=True, blank=True)
    nhacungcap = models.ForeignKey(company_vendor, on_delete=models.SET_NULL, null=True, blank=True)
    nhachinh = models.ForeignKey(company_supplier, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.ma_nhanvien}"

class operator_history(models.Model):
    operator = models.ForeignKey(company_operator, on_delete=models.CASCADE, related_name="work_histories")
    customer = models.ForeignKey(company_customer, on_delete=models.CASCADE, related_name="operator_histories")
    vendor = models.ForeignKey(company_vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="operator_histories")
    
    start_date = models.DateTimeField(null=True, blank=True)  # Thời gian bắt đầu làm việc
    end_date = models.DateTimeField(null=True, blank=True)    # Thời gian kết thúc làm việc
    notes = models.TextField(null=True, blank=True)           # Ghi chú thêm nếu cần

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']  # Sắp xếp theo thời gian bắt đầu mới nhất
        verbose_name = "Operator History"
        verbose_name_plural = "Operator Histories"

    def __str__(self):
        return f"{self.operator} -> {self.customer} ({self.start_date} - {self.end_date})"
