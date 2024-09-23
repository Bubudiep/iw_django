from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ForeignKey('Photos', on_delete=models.SET_NULL, null=True, blank=True, related_name='avatar_profiles')
    wallpaper = models.ForeignKey('Photos', on_delete=models.SET_NULL, null=True, blank=True, related_name='wallpaper_profiles')
    zalo_id = models.CharField(max_length=50, null=True, blank=True)
    zalo_name = models.CharField(max_length=50, null=True, blank=True)
    zalo_avatar = models.CharField(max_length=250, null=True, blank=True)
    zalo_phone = models.CharField(max_length=50, null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=225, null=True, blank=True)
    huyen = models.CharField(max_length=150, null=True, blank=True)
    tinh = models.CharField(max_length=150, null=True, blank=True)
    long_pos = models.CharField(max_length=50, null=True, blank=True)
    lat_pos = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.zalo_id

class Album(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Photos(models.Model):
    is_active = models.BooleanField(default=True)
    filename = models.CharField(max_length=150, null=True, blank=True)
    filesize = models.CharField(max_length=150, null=True, blank=True)
    data = models.TextField(null=True, blank=True)  # Lưu ảnh dưới dạng base64
    data_mini = models.TextField(null=True, blank=True)  # Lưu ảnh dưới dạng base64
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

class WorkSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worksheets')
    company = models.CharField(max_length=255, null=True, blank=True)
    jobs_title = models.CharField(max_length=255, null=True, blank=True)
    working_day = models.IntegerField(default=0)
    ngay_nghi = models.CharField(max_length=255, null=True, blank=True)
    calamviec = models.CharField(max_length=255, null=True, blank=True)
    finish_working_day = models.IntegerField(default=0)
    start_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    qr_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        allowed_ngay_nghi_values = ['CN', 'T7CN']
        if self.ngay_nghi and self.ngay_nghi not in allowed_ngay_nghi_values:
            raise ValueError(f"Invalid value for ngay_nghi: {self.ngay_nghi}. Allowed values are: {allowed_ngay_nghi_values}")

        allowed_calamviec_values = ['HC', '2Ca', '3Ca']
        if self.calamviec and self.calamviec not in allowed_calamviec_values:
            raise ValueError(f"Invalid value for calamviec: {self.calamviec}. Allowed values are: {allowed_calamviec_values}")

    def __str__(self):
        return f"WorkSheet for {self.user}"

class CongTy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_congty')
    tencongty = models.CharField(max_length=255, null=True, blank=True)
    bophan = models.CharField(max_length=255, null=True, blank=True)
    chucvu = models.CharField(max_length=255, null=True, blank=True)
    batdau_dilam = models.DateTimeField(default=timezone.now, null=True, blank=True)
    ketthuc_dilam = models.DateTimeField(default=None, null=True, blank=True)
    condilam = models.BooleanField(default=True)
    qr_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user} - {self.tencongty}"

class Quydinh(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_quydinh')
    congty = models.ForeignKey(CongTy, on_delete=models.CASCADE, related_name='congty_quydinh')
    tenquydinh = models.CharField(max_length=255, null=True, blank=True)
    online = models.BooleanField(default=True)
    qr_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nguoitao} - {self.tenquydinh}"

class PhanloaiNgay(models.Model):
    quydinh = models.ForeignKey(Quydinh, on_delete=models.CASCADE, related_name='quydinh_phanloaingay')
    tenloaingay = models.CharField(max_length=255, null=True, blank=True)
    uutien = models.IntegerField(default=0, null=True, blank=True)
    heso = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nguoitao} - {self.tenloaingay}"
    
class ChitietNgay(models.Model):
    loaingay = models.ForeignKey(PhanloaiNgay, on_delete=models.CASCADE)
    theongaycuthe = models.BooleanField(default=True) # true thì sẽ theo trường ngày cụ thể / theo ngay trong tuan
    ngaycuthe = models.DateField(default=timezone.now, null=True, blank=True)
    ngaytrongtuan = models.TextField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.id}"

class PhanloaiCa(models.Model):
    quydinh = models.ForeignKey(Quydinh, on_delete=models.CASCADE)
    tenca = models.CharField(max_length=255, null=True, blank=True)
    ghichu = models.TextField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nguoitao} - {self.tenca}"

class Calamviec(models.Model):
    loaingay = models.ForeignKey(PhanloaiNgay, on_delete=models.CASCADE)
    loaica = models.ForeignKey(PhanloaiCa, on_delete=models.CASCADE)
    batdau = models.DateTimeField(default=timezone.now, null=True, blank=True)
    ketthuc = models.DateTimeField(default=timezone.now, null=True, blank=True)
    heso = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user} - {self.tencongty}"

class ChitietCalamviec(models.Model):
    calamviec = models.ForeignKey(Calamviec, on_delete=models.CASCADE, related_name='chitiet_calamviec')
    batdau = models.DateTimeField(default=timezone.now, null=True, blank=True)
    ketthuc = models.DateTimeField(default=timezone.now, null=True, blank=True)
    heso = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.calamviec} - {self.heso}"

class Bangluong(models.Model):
    congty = models.ForeignKey(CongTy, on_delete=models.CASCADE, related_name='congty_bangluong')
    tenbangluong = models.CharField(max_length=255, null=True, blank=True)
    ngaychotcong = models.IntegerField(default=1, null=True, blank=True)
    ghichu = models.CharField(max_length=255, null=True, blank=True)
    online = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user} - {self.tencongty}"

class BangluongChitiet(models.Model):
    bangluong = models.ForeignKey(Bangluong, on_delete=models.CASCADE, related_name='bangluong_chitiet')
    tenluong = models.CharField(max_length=255, null=True, blank=True)
    mucluong = models.FloatField(default=0,max_length=255, null=True, blank=True)
    tinhvaotangca = models.BooleanField(default=True)
    batbuocdilamdusongay = models.BooleanField(default=True)
    songayphaidilamdu = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user} - {self.tencongty}"

class WorkSalary(models.Model):
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE, related_name='work_salaries')
    salary_name = models.CharField(max_length=255, null=True, blank=True)
    salary = models.IntegerField(default=0, null=True, blank=True)
    is_monthly = models.BooleanField(default=False)
    is_tangca = models.BooleanField(default=True)
    checked_date = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.salary_name

class WorkRecord(models.Model):
    LEAVE_TYPES = [
        (0, 'Không phép'),
        (1, 'Có phép'),
        (2, 'Hưởng lương'),
        (3, 'Nghỉ ốm')
    ]

    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE, related_name='work_records')
    leave_type = models.IntegerField(choices=LEAVE_TYPES, null=True, blank=True)
    bonus_salary = models.IntegerField(null=True, blank=True)
    giobinhthuong = models.FloatField(default=0, null=True, blank=True)
    giotangca = models.FloatField(default=0, null=True, blank=True)
    heso = models.FloatField(default=100, null=True, blank=True)
    work_date = models.DateField(default=timezone.now)
    is_working = models.BooleanField(default=True)
    off_special = models.BooleanField(default=False)
    off_rate = models.FloatField(default=0, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    over_time = models.FloatField(default=0, null=True, blank=True)
    late_time = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WorkRecord for {self.worksheet.user}"

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True) # Người đăng ký
    name = models.CharField(max_length=255)
    sorted_name = models.CharField(max_length=255,null=True, blank=True)
    masothue = models.CharField(max_length=255,unique=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.companyName
    
class CompanyWokingday(models.Model): # Hệ số các ngày trong tuần
    company = models.OneToOneField(Company, on_delete=models.CASCADE,null=True, blank=True)
    workDay = models.CharField(max_length=255,null=True,blank=True) # T2, T3, T4, T5, T6, T7, CN
    rate = models.FloatField(default=100,null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.companyName
    
class CompanyWorkshift(models.Model): # Các ca làm việc và hệ số chung của ca làm việc
    workDay = models.ForeignKey(CompanyWokingday, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    startTime = models.TimeField(default="08:00:00")
    finishTime = models.TimeField(default="17:00:00")

    rate = models.FloatField(default=100,null=True, blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
class CompanyWorkshiftFreetime(models.Model): # Giờ nghỉ giải lao của các ca làm việc
    workshift = models.ForeignKey(CompanyWorkshift, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255) # nghỉ giữa giờ, nghỉ ăn trưa
    startTime = models.TimeField(default="10:00:00")
    finishTime = models.TimeField(default="10:15:00")
    isPay = models.BooleanField(default=False) # được tính tiền hay không
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class CompanyWorkrate(models.Model):
    workshift = models.ForeignKey(CompanyWorkshift, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    startTime = models.TimeField(default="08:00:00")
    finishTime = models.TimeField(default="17:00:00")

    rate = models.FloatField(default=100,null=True, blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
class CompanySalaryFormat(models.Model): # Format lương cụ thể của công ty
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255) # Tên của lương (lương cơ bản, phụ cấp,....)
    is_Overtime = models.BooleanField(default=True) # Có được tính vào tăng ca hay không
    default_value = models.FloatField(default=0, null=True, blank=True) # Mức lương mặc định của tên lương đấy
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True) # Người thêm
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.salaryRule.name}_{self.name}"
    
class CompanySalaryFormatConditional(models.Model): # Điều kiện tính lương
    salaryFormat = models.ForeignKey(CompanySalaryFormat, on_delete=models.CASCADE,null=True, blank=True)
    workDay = models.IntegerField(default=0)
    rate = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.salaryFormat.name}_{self.workDay}"
    
class CompanySalaryRule(models.Model): # Rule lương của công ty cho cá nhân hoặc tập thể
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.company.companyName}_{self.name}"
    
class CompanySalaryDetails(models.Model): # Chi tiết lương của cái rule đó
    salaryRule = models.ForeignKey(CompanySalaryRule, on_delete=models.CASCADE,null=True, blank=True)
    salaryFormat = models.ForeignKey(CompanySalaryFormat, on_delete=models.CASCADE,null=True, blank=True)
    value = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.salaryRule.name}_{self.name}"
    
class CompanyDepartment(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)  # Tên phòng ban
    description = models.TextField(null=True, blank=True)  # Mô tả phòng ban
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}_{self.name}"
# Model Chức vụ
class CompanyPosition(models.Model):
    department = models.ForeignKey(CompanyDepartment, on_delete=models.CASCADE,null=True, blank=True)
    title = models.CharField(max_length=100, unique=True)  # Tên chức vụ
    description = models.TextField(null=True, blank=True)  # Mô tả chức vụ
    salary = models.ForeignKey(CompanySalaryRule, on_delete=models.SET_NULL, null=True)  # Liên kết đến mức lương
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
# Model Nhân viên
class CompanyEmployee(models.Model):
    app_level_CHOICES = (
        ['admin', 'admin'],
        ['staff', 'staff'],
        ['normal', 'normal']
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="CompanyEmployee_bind")
    full_name = models.CharField(max_length=50)  # Tên nhân viên
    is_active = models.BooleanField(default=True)  # Trạng thái làm việc
    is_online = models.BooleanField(default=True)  # Trạng thái đi làm
    email = models.EmailField(unique=True)  # Email nhân viên
    address = models.TextField(null=True, blank=True)  # Địa chỉ nhân viên
    position = models.ForeignKey(CompanyPosition, on_delete=models.SET_NULL, null=True)  # Chức vụ
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Số điện thoại
    bank_name = models.CharField(max_length=200, null=True, blank=True)  # tên ngân hàng
    bank_code = models.CharField(max_length=30, null=True, blank=True)  # code ngân hàng
    bank_number = models.CharField(max_length=20, null=True, blank=True)  # tài khoản ngân hàng
    hire_date = models.DateField()  # Ngày tuyển dụng
    app_level = models.CharField(max_length=255, choices=app_level_CHOICES, default='normal', null=True, blank=True)
    personal_salary = models.ForeignKey(CompanySalaryRule, on_delete=models.SET_NULL, null=True)  # Liên kết đến mức lương

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="CompanyEmployee_created")  # Liên kết đến tài khoản của nhân viên
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def get_final_salary(self):
        if self.personal_salary:
            return self.personal_salary
        if self.position and self.position.salary:
            return self.position.salary
        return None  # Nếu không có thông tin lương, trả về 0
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
