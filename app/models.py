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
