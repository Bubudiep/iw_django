from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from datetime import time

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
    is_public = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Photos(models.Model):
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    filename = models.CharField(max_length=150, null=True, blank=True)
    filesize = models.CharField(max_length=150, null=True, blank=True)
    data = models.TextField(null=True, blank=True)  # Lưu ảnh dưới dạng base64
    data_mini = models.TextField(null=True, blank=True)  # Lưu ảnh dưới dạng base64
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename
    
class Tuchamcong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    tencongty = models.CharField(max_length=150, null=True, blank=True)
    ngaybatdau = models.DateField(default=lambda: timezone.now().date())
    bophan = models.CharField(max_length=150, null=True, blank=True)
    chucvu = models.CharField(max_length=150, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  f"{self.tencongty}_{self.user.username}"
    
class Tutinhluong(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    tenluong = models.CharField(max_length=150, null=True, blank=True)
    tinhvaotangca = models.BooleanField(default=True)
    phaidilamdu = models.BooleanField(default=True)
    socongyeucau = models.IntegerField(default=0, null=True, blank=True)
    luong = models.FloatField(default=0, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenluong}_{self.tuchamcong.tencongty}"
    
class TutinhChuyencan(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    socongyeucau = models.IntegerField(default=26)
    tienchuyencan = models.FloatField(default=0)
    nghi1ngay = models.FloatField(default=0)
    nghi2ngay = models.FloatField(default=0)
    nghi3ngay = models.FloatField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}_{self.tuchamcong.tencongty}"
    
def default_giovao():
    today = timezone.now().date()
    return timezone.make_aware(datetime.combine(today, time(8, 0, 0)))

def default_giora():
    today = timezone.now().date()
    return timezone.make_aware(datetime.combine(today, time(17, 0, 0)))

class Tuchamcongtay(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    ngay = models.DateField(default=timezone.now)
    giovao = models.DateTimeField(default=default_giovao)  # Set default to 08:00:00
    giora = models.DateTimeField(default=default_giora)  # Set default to 17:00:00
    tangca = models.FloatField(default=0)
    vaomuon = models.FloatField(default=0)
    giolam = models.FloatField(default=0)
    dilam = models.BooleanField(default=True)
    nghicoluong = models.BooleanField(default=True)
    nghicochuyencan = models.BooleanField(default=True)
    ghichu = models.TextField(default=None)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ngay}_{self.tuchamcong.tencongty}"
    
class Kieungay(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    tenloaingay = models.CharField(max_length=200, null=True, blank=True)
    ghichu = models.TextField(default=None, null=True, blank=True)
    ngaycuthe = models.TextField(default=None, null=True, blank=True)
    cochuyencan = models.BooleanField(default=False)
    ngaytrongtuan = models.TextField(default=None, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenloaingay}_{self.tuchamcong.tencongty}"
    
class Kieuca(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    tenca = models.CharField(max_length=200, null=True, blank=True)
    ghichu = models.TextField(default=None, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenca}_{self.tuchamcong.tencongty}"
    
class Heso(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    kieungay = models.ForeignKey(Kieungay, on_delete=models.CASCADE)
    kieuca = models.ForeignKey(Kieuca, on_delete=models.CASCADE)
    batdau = models.TimeField(default="08:00:00", null=True, blank=True)  # Set default to 08:00:00
    ketthuc = models.TimeField(default="17:00:00", null=True, blank=True)  # Set default to 17:00:00
    heso = models.FloatField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.heso}_{self.tuchamcong.tencongty}"
    