from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from datetime import time
import uuid  # Thư viện để tạo khóa ngẫu nhiên

def get_current_date():
    return timezone.now().date()

class Fixed_link(models.Model):
    app = models.CharField(max_length=100,blank=True, null=True)  # Tên quán ăn
    platform = models.CharField(max_length=100,blank=True, null=True)  # Tên quán ăn
    link = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    def __str__(self):
        return f"{self.app}_{self.platform}"
    
class QR_Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    QRKey = models.CharField(max_length=32, unique=True, editable=False, blank=True, null=True)
    isSuccess = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.QRKey:
            self.QRKey = uuid.uuid4().hex.upper()  # Tạo UUID, xóa dấu '-' và chuyển sang viết hoa
        super(QR_Login, self).save(*args, **kwargs)
        
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
    level = models.IntegerField(default=0, null=True, blank=True)
    is_Chutro=models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return self.zalo_id

class Album(models.Model):
    name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

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
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return self.filename
    
class Tuchamcong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    tencongty = models.CharField(max_length=150, null=True, blank=True)
    ngaybatdau = models.DateField(default=get_current_date)
    bophan = models.CharField(max_length=150, null=True, blank=True)
    chucvu = models.CharField(max_length=150, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

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
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

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
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.id}_{self.tuchamcong.tencongty}"
    
def default_giovao():
    today = timezone.now().date()
    return timezone.make_aware(datetime.combine(today, time(8, 0, 0)))

def default_giora():
    today = timezone.now().date()
    return timezone.make_aware(datetime.combine(today, time(17, 0, 0)))

class Kieungay(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    tenloaingay = models.CharField(max_length=200, null=True, blank=True)
    ghichu = models.TextField(default=None, null=True, blank=True)
    ngaycuthe = models.TextField(default=None, null=True, blank=True)
    cochuyencan = models.BooleanField(default=False)
    ngaytrongtuan = models.TextField(default=None, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tenloaingay}_{self.tuchamcong.tencongty}"
    
class Kieuca(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    tenca = models.CharField(max_length=200, null=True, blank=True)
    ghichu = models.TextField(default=None, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tenca}_{self.tuchamcong.tencongty}"
    
class Tuchamcongtay(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    ca = models.ForeignKey(Kieuca, on_delete=models.SET_NULL, null=True, blank=True)
    kieungay = models.ForeignKey(Kieungay, on_delete=models.SET_NULL, null=True, blank=True)
    ngay = models.DateField(default=timezone.now)
    giovao = models.DateTimeField(default=default_giovao)  # Set default to 08:00:00
    giora = models.DateTimeField(default=default_giora)  # Set default to 17:00:00
    tangca = models.FloatField(default=0)
    vaomuon = models.FloatField(default=0)
    giolam = models.FloatField(default=0)
    dilam = models.BooleanField(default=True, null=True, blank=True)
    nghicoluong = models.BooleanField(default=True, null=True, blank=True)
    nghicochuyencan = models.BooleanField(default=True, null=True, blank=True)
    ghichu = models.TextField(default=None, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.ngay}_{self.tuchamcong.tencongty}"
    
class Heso(models.Model):
    tuchamcong = models.ForeignKey(Tuchamcong, on_delete=models.CASCADE)
    kieungay = models.ForeignKey(Kieungay, on_delete=models.CASCADE)
    kieuca = models.ForeignKey(Kieuca, on_delete=models.CASCADE)
    batdau = models.TimeField(default="08:00:00", null=True, blank=True)  # Set default to 08:00:00
    ketthuc = models.TimeField(default="17:00:00", null=True, blank=True)  # Set default to 17:00:00
    heso = models.FloatField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.heso}_{self.tuchamcong.tencongty}"
    
## Doanh nghiệp
class Congty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    QRcode = models.CharField(max_length=200, null=True, blank=True)
    
    tencongty = models.CharField(max_length=200, null=True, blank=True)
    tendaydu = models.TextField(null=True, blank=True)
    diachi = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    loaihinhkinhdoanh = models.CharField(max_length=200, null=True, blank=True)
    danhmuc = models.CharField(max_length=200, null=True, blank=True)
    daxacminh = models.BooleanField(default=False, null=True, blank=True)
    doitac = models.BooleanField(default=False, null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    wallpaper = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tencongty}"
    
class Quydinh(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    
    tenquydinh = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tenquydinh}"
    
class Chiaca(models.Model):
    quydinh = models.ForeignKey(Quydinh, on_delete=models.CASCADE)
    
    tenca = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tenca}"
    
class Chiangay(models.Model):
    quydinh = models.ForeignKey(Quydinh, on_delete=models.CASCADE)
    
    tenngay = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tenngay}"
    
class Phanloaingay(models.Model):
    ngaylamviec = models.ForeignKey(Chiangay, on_delete=models.CASCADE)
    
    ngaycuthe = models.TextField(null=True, blank=True) # [YYYY-MM-DD,date,date,date]
    ngaytrongtuan = models.TextField(null=True, blank=True) # [T2,T3,T4,T5,T6,T7,CN]
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.tenngay}"
    
class Chiacatheongay(models.Model):
    ngaylamviec = models.ForeignKey(Chiangay, on_delete=models.CASCADE)
    calamviec = models.ForeignKey(Chiaca, on_delete=models.CASCADE)
    
    batdau = models.TimeField(max_length=200, null=True, blank=True)
    ketthuc = models.TimeField(max_length=200, null=True, blank=True)
    ketthucvaongayhomsau=models.BooleanField(default=False, null=True,blank=True)
    heso = models.FloatField(default=1, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.ngaylamviec.tenngay}_{self.calamviec.tenca}"
    
class ChitieChiacatheongay(models.Model):
    Chiacatheongay = models.ForeignKey(Chiacatheongay, on_delete=models.CASCADE)
    batdau = models.TimeField(max_length=200, null=True, blank=True)
    ketthuc = models.TimeField(max_length=200, null=True, blank=True)
    ketthucvaongayhomsau=models.BooleanField(default=False, null=True,blank=True)
    heso = models.FloatField(default=1, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.Chiacatheongay.ngaylamviec.tenngay}_{self.Chiacatheongay.calamviec.tenca}_{self.id}"

class Bophan(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    bophancha = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    tenbophan = models.CharField(max_length=200, null=True, blank=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenbophan}"

class Capbac(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    heso = models.IntegerField(default=0, null=True, blank=True)
    
    tencapbac = models.CharField(max_length=200, null=True, blank=True)
    codecapbac = models.CharField(max_length=200, null=True, blank=True)
    mucluongthapnhat = models.IntegerField(default=0, null=True, blank=True)
    mucluongcaonhat = models.IntegerField(default=0, null=True, blank=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tencapbac}"

class Chucvu(models.Model):
    bophan = models.ForeignKey(Bophan, on_delete=models.CASCADE)
    capbac = models.ForeignKey(Capbac, on_delete=models.CASCADE, null=True, blank=True)
    
    tenchucvu = models.CharField(max_length=200, null=True, blank=True)
    chucvucha = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenchucvu}"

class BangluongTheochucvu(models.Model):
    chucvu = models.ForeignKey(Chucvu, on_delete=models.CASCADE)
    tenluong = models.CharField(max_length=200, null=True, blank=True)
    mucluong = models.IntegerField(null=True, blank=True)
    tinhvaotangca = models.BooleanField(default=False, null=True, blank=True)
    tinhthue = models.BooleanField(default=False, null=True, blank=True)
    tinhbaohiem = models.BooleanField(default=False, null=True, blank=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenluong}"

class ThuongtheoChucvu(models.Model):
    chucvu = models.ForeignKey(Chucvu, on_delete=models.CASCADE)
    tenthuong = models.CharField(max_length=200, null=True, blank=True)
    mucthuong = models.IntegerField(null=True, blank=True)
    tinhvaotangca = models.BooleanField(default=False, null=True, blank=True)
    tinhthue = models.BooleanField(default=False, null=True, blank=True)
    tinhbaohiem = models.BooleanField(default=False, null=True, blank=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenthuong}"
    
class Nhanvien(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # cho phép người dùng liên kết;
    manhanvien = models.CharField(max_length=200, null=True, blank=True)
    chucvu = models.ForeignKey(Chucvu, on_delete=models.SET_NULL, null=True, blank=True)
    capbac = models.ForeignKey(Capbac, on_delete=models.SET_NULL, null=True, blank=True)

    condilam = models.BooleanField(default=True, null=True, blank=True)
    ngaybatdau = models.DateField(null=True, blank=True)
    ngayketthuc = models.DateField(null=True, blank=True)
    macccd = models.CharField(max_length=200, null=True, blank=True)
    hovaten = models.CharField(max_length=200, null=True, blank=True)
    ngaysinh = models.DateField(null=True, blank=True)
    hovaten = models.CharField(max_length=200, null=True, blank=True)
    diachi = models.CharField(max_length=200, null=True, blank=True)
    isMale = models.BooleanField(default=True, null=True, blank=True)
    dakethon = models.BooleanField(default=True, null=True, blank=True)
    key = models.CharField(max_length=200, null=True, blank=True)

    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.manhanvien}"
    
class Thumuc(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    thumucgoc = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    tenthumuc = models.CharField(max_length=200, null=True, blank=True)
    isPublic = models.BooleanField(default=False, null=True, blank=True)
    isLock = models.BooleanField(default=False, null=True, blank=True)
    minLevel = models.ForeignKey(Capbac, on_delete=models.SET_NULL, null=True, blank=True)
    mota = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenthumuc}"
    
class Tailieu(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    thumucgoc = models.ForeignKey(Thumuc, on_delete=models.CASCADE)
    
    tenfile = models.CharField(max_length=200, null=True, blank=True)
    tenfilefull = models.CharField(max_length=200, null=True, blank=True)
    filetype = models.CharField(max_length=200, null=True, blank=True)
    filesize = models.CharField(max_length=200, null=True, blank=True)
    filelink = models.CharField(max_length=200, null=True, blank=True)
    base64data = models.CharField(max_length=200, null=True, blank=True)
    isTrash = models.BooleanField(default=False, null=True, blank=True)
    isLock = models.BooleanField(default=False, null=True, blank=True)
    minLevel = models.ForeignKey(Capbac, on_delete=models.SET_NULL, null=True, blank=True)
    mota = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenfile}"
    
class DateMark(models.Model):
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    markname = models.CharField(max_length=250,unique=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.markname}"
    
class MarkConfig(models.Model):
    mark = models.ForeignKey(DateMark,on_delete=models.CASCADE)
    ngaycong = models.FloatField(default=0,null=True,blank=True)
    checkgiocong = models.BooleanField(default=True,null=True)
    giocongcongthem = models.FloatField(default=0,null=True,blank=True)
    cochuyencan = models.BooleanField(default=False,null=True)
    cophep = models.BooleanField(default=False,null=True)
    heso = models.FloatField(default=1,null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.mark.markname}_config"

class Chamcong(models.Model):
    mark = models.ForeignKey(DateMark,on_delete=models.SET_NULL, null=True, blank=True)
    nhanvien = models.ForeignKey(Nhanvien,on_delete=models.CASCADE)
    calamviec = models.CharField(max_length=100, null=True, blank=True)
    ngaylamviec = models.DateField(null=True, blank=True)
    gioBatdau = models.DateTimeField(null=True, blank=True)
    gioKetthuc = models.DateTimeField(null=True, blank=True)
    giolamviecHC = models.FloatField(default=8,null=True, blank=True) # số giờ được tính, max 8
    giolamviecTC = models.FloatField(default=0,null=True, blank=True) # số giờ tăng ca
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.nhanvien.manhanvien}"
    
class PhanloaiBatthuong(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    congty = models.ForeignKey(Congty, on_delete=models.CASCADE)
    tenloai = models.CharField(max_length=200,null=True, blank=True)
    codeloai = models.CharField(max_length=200,null=True, blank=True)
    ghichu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenloai}"
    
class Batthuong(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    isChonguoikhac = models.BooleanField(default=False, null=True, blank=True)
    nhanvien = models.ForeignKey(Nhanvien,on_delete=models.SET_NULL, null=True, blank=True)
    loaibatthuong = models.ForeignKey(PhanloaiBatthuong, on_delete=models.SET_NULL, null=True, blank=True)
    tieude = models.CharField(max_length=200, null=True, blank=True)
    noidung = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.nhanvien}"
    
class BathuongHistory(models.Model):
    batthuong = models.ForeignKey(Batthuong,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    action = models.CharField(max_length=200, null=True, blank=True)
    old_data = models.TextField(null=True, blank=True)
    new_data = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.batthuong.nhanvien}"




class Nhatro(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    tenTro = models.CharField(max_length=200, null=True, blank=True)
    anhDaidien = models.ForeignKey(Photos,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    isActive = models.BooleanField(default=True, blank=True)
    isLock = models.BooleanField(default=False, blank=True)
    tienphong=models.FloatField(default=0, null=True, blank=True)
    tienrac=models.FloatField(default=0, null=True, blank=True)
    tiennuoc=models.FloatField(default=0, null=True, blank=True)
    tiendien=models.FloatField(default=0, null=True, blank=True)
    tienkhac=models.FloatField(default=0, null=True, blank=True)
    isBand = models.BooleanField(default=False, blank=True)
    giaphongThapnhat = models.FloatField(default=0, null=True, blank=True)
    giaphongCaonhat = models.FloatField(default=0, null=True, blank=True)
    chungchu = models.BooleanField(default=0, null=True, blank=True) # có chung chủ hay không
    wifi = models.BooleanField(default=0, null=True, blank=True)
    dieuhoa = models.BooleanField(default=0, null=True, blank=True)
    nonglanh = models.BooleanField(default=0, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    diachi = models.CharField(max_length=200, null=True, blank=True)
    mota = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    QRKey = models.CharField(max_length=32, unique=True, editable=False, blank=True, null=True)
     # New field for maximum payment collection date
    ngay_thu_tien = models.PositiveSmallIntegerField(default=15, blank=True)  # Default is day 31
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.tenTro}"
    def save(self, *args, **kwargs):
        if not self.QRKey:
            self.QRKey = uuid.uuid4().hex.upper()  # Tạo UUID, xóa dấu '-' và chuyển sang viết hoa
        super(Nhatro, self).save(*args, **kwargs)

class NhatroNoiquy(models.Model):
    nhaTro = models.ForeignKey(Nhatro,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    noiquy = models.TextField(null=True, blank=True)
    tienphat = models.FloatField(default=0, null=True, blank=True)
    mota = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.nhaTro.tenTro}"
    
class NhatroThongtin(models.Model):
    nhaTro = models.ForeignKey(Nhatro,on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    tienKhac = models.FloatField(default=0, null=True, blank=True)
    tienRac = models.FloatField(default=0, null=True, blank=True)
    tienDien = models.FloatField(default=0, null=True, blank=True)
    tienNuoctheothang = models.FloatField(default=0, null=True, blank=True)
    tienNuoc = models.FloatField(default=0, null=True, blank=True)
    lat_post = models.CharField(max_length=200, null=True, blank=True)
    long_post = models.CharField(max_length=200, null=True, blank=True)
    mota = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"{self.nhaTro.tenTro}"
    
class Tang(models.Model):
    nhaTro = models.ForeignKey(Nhatro, on_delete=models.CASCADE, related_name='tangs')  # Nhà trọ
    tenTang = models.CharField(max_length=10)  # Số tầng
    mota = models.TextField(null=True, blank=True)  # Mô tả tầng
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"Tầng {self.tenTang} - {self.nhaTro.tenTro}"

class Phong(models.Model):
    tang = models.ForeignKey(Tang, on_delete=models.CASCADE, related_name='phongs')  # Tầng chứa phòng
    soPhong = models.CharField(max_length=10)  # Số phòng
    giaPhong = models.FloatField(default=None, null=True, blank=True)  # Giá phòng
    giaDien = models.FloatField(default=None, null=True, blank=True)  # Giá phòng
    giaNuoc = models.FloatField(default=None, null=True, blank=True)  # Giá phòng
    giaRac = models.FloatField(default=None, null=True, blank=True)  # Giá phòng
    giaKhac = models.FloatField(default=None, null=True, blank=True)  # Giá phòng
    wifi = models.BooleanField(default=None, null=True, blank=True)
    dieuhoa = models.BooleanField(default=None, null=True, blank=True)
    nonglanh = models.BooleanField(default=None, null=True, blank=True)
    soNguoiToida = models.IntegerField(default=1)  # Số người ở tối đa
    isActive = models.BooleanField(default=True, blank=True)
    mota = models.TextField(null=True, blank=True)  # Mô tả phòng
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return f"Phòng {self.soPhong} - Tầng {self.tang.tenTang} - {self.tang.nhaTro.tenTro}"

class Nguoitro(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL,null=True, blank=True)  # Liên kết với tài khoản người dùng
    hoTen = models.CharField(max_length=200, null=True, blank=True)
    sdt = models.CharField(max_length=15, null=True, blank=True)  # Số điện thoại
    cccd = models.CharField(max_length=12, null=True, blank=True)  # Căn cước công dân
    quequan = models.CharField(max_length=255, null=True, blank=True)  # Số điện thoại
    ngaysinh = models.DateTimeField(null=True, blank=True)  # Căn cước công dân
    isActive = models.BooleanField(default=True)  # Trạng thái người dùng
    tamtru = models.BooleanField(default=False)  # Trạng thái người dùng
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.hoTen}"

class LichsuNguoitro(models.Model):
    nguoiTro = models.ForeignKey(Nguoitro, on_delete=models.SET_NULL,null=True, blank=True)  # Người ở trọ
    phong = models.ForeignKey(Phong, on_delete=models.SET_NULL,null=True, blank=True)  # Phòng trọ đang ở
    isOnline = models.BooleanField(default=True)
    ngayBatdauO = models.DateField(null=True, blank=True)  # Ngày bắt đầu ở trọ
    ngayKetthucO = models.DateField(null=True, blank=True)  # Ngày kết thúc ở trọ
    tiencoc = models.FloatField(default=0,null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.nguoiTro.hoTen}"
    
class LichsuThanhToan(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)  # Liên kết với tài khoản người dùng
    phong = models.ForeignKey(Phong, on_delete=models.SET_NULL, null=True, blank=True)
    nguoiTro = models.ForeignKey(Nguoitro, on_delete=models.SET_NULL, null=True, blank=True)
    soTienPhong = models.FloatField(default=0, null=True, blank=True)
    soTienDien = models.FloatField(default=0, null=True, blank=True)
    soTienNuoc = models.FloatField(default=0, null=True, blank=True)
    soTienWifi = models.FloatField(default=0, null=True, blank=True)
    soTienRac = models.FloatField(default=0, null=True, blank=True)
    soTienKhac = models.FloatField(default=0, null=True, blank=True)
    tongTien = models.FloatField(default=0, null=True, blank=True)
    ngayThanhToan = models.DateTimeField(null=True, blank=True)  # Ngày thanh toán
    ngayKetthuc = models.DateField(null=True, blank=True)  # Ngày thanh toán
    ngayBatdau = models.DateField(null=True, blank=True)  # Ngày thanh toán
    isPaid = models.BooleanField(default=False)  # Trạng thái thanh toán
    ghichu = models.TextField(null=True, blank=True)  # Ghi chú
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    Key = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def save(self, *args, **kwargs):
        if not self.Key:
            tkey=uuid.uuid4().hex[:18].upper()
            self.Key = f"HD-{tkey}"
        super(LichsuThanhToan, self).save(*args, **kwargs)

    def mark_as_paid(self):
        self.isPaid = True
        self.ngayThanhToan = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.ngayThanhToan if self.isPaid else 'Chưa thanh toán'}"

class LichsuTieuThu(models.Model):
    phong = models.ForeignKey(Phong, on_delete=models.SET_NULL, null=True, blank=True)  # Phòng trọ liên quan
    hoadon = models.ForeignKey(LichsuThanhToan, on_delete=models.SET_NULL,null=True, blank=True)  # Liên kết với tài khoản người dùng
    soDienKetthuc = models.FloatField(default=0, null=True, blank=True)  # Số điện tiêu thụ trong tháng
    soNuocKetthuc = models.FloatField(default=0, null=True, blank=True)  # Số nước tiêu thụ trong tháng
    ngaBatdau = models.DateTimeField(null=True, blank=True)  # Ngày thanh toán
    ngayKetthuc = models.DateField(null=True, blank=True)  # Ngày thanh toán
    thang = models.DateField(null=True, blank=True)  # Tháng của bản ghi tiêu thụ
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"Tiêu thụ: {self.nguoiTro.hoTen} - Phòng {self.phong.soPhong} - Tháng {self.thang}"

class ChiTietThanhToan(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)  # Liên kết với tài khoản người dùng
    nguoiTro = models.ForeignKey(Nguoitro, on_delete=models.SET_NULL,null=True, blank=True)  # Người ở trọ
    lichsu_thanh_toan = models.ForeignKey(LichsuThanhToan, on_delete=models.CASCADE, related_name='chi_tiet_thanh_toan')
    so_tien = models.FloatField(default=0)  # Số tiền thanh toán cho hạng mục
    ghichu = models.TextField(null=True, blank=True)  # Ghi chú
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.so_tien} VND"



#### chấm công đi làm
class DanhsachCongty(models.Model):
    congty =  models.CharField(max_length=200, null=True, blank=True)
    isActive =  models.BooleanField(default=True, null=True, blank=True)
    isBaned =  models.BooleanField(default=True, null=True, blank=True)
    ghichu =  models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.congty}"

class DanhsachAdmin(models.Model):
    congty = models.ForeignKey(DanhsachCongty, on_delete=models.CASCADE)
    zalo_id = models.CharField(max_length=200, null=True, blank=True)
    isAdmin =  models.BooleanField(default=True, null=True, blank=True)
    isStaff =  models.BooleanField(default=True, null=True, blank=True)
    ghichu =  models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.congty}_{self.zalo_id}"

class DanhsachNhanvien(models.Model):
    congty = models.ForeignKey(DanhsachCongty, on_delete=models.SET_NULL, null=True, blank=True)
    manhanvien = models.CharField(max_length=200, unique=True, null=True, blank=True)
    HovaTen =  models.CharField(max_length=200, null=True, blank=True)
    nguoituyen =  models.CharField(max_length=200, null=True, blank=True)
    ghichu =  models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.congty}_{self.manhanvien}"

class DanhsachnhanvienDilam(models.Model):
    manhanvien = models.ForeignKey(DanhsachNhanvien, on_delete=models.CASCADE)
    chamcongdi =  models.BooleanField(default=True, null=True, blank=True) # True là đi làm, False là đi về
    ngaydilam =  models.DateField(max_length=200, null=True, blank=True)
    giochamcong =  models.DateTimeField(default=timezone.now,max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định

    def __str__(self):
        return f"{self.manhanvien.manhanvien}_{self.ngaydilam}"
    
class Restaurant(models.Model):
    address_details = models.JSONField(blank=True, null=True)
    name = models.CharField(max_length=100)  # Tên quán ăn
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)  # Số điện thoại quán ăn
    mohinh = models.CharField(max_length=200,blank=True, null=True)
    avatar = models.TextField(blank=True, null=True)
    Oder_online = models.BooleanField(default=True)
    Takeaway = models.BooleanField(default=True)
    isRate = models.BooleanField(default=True)
    isChat = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    class Meta:
        ordering = ['-id']  # Sắp xếp theo 'id' mặc định
    def __str__(self):
        return self.name
      
class Restaurant_socket(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)  # Mô tả thêm về quán ăn
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    QRKey = models.CharField(max_length=32, unique=True, editable=False, blank=True, null=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']
    def save(self, *args, **kwargs):
        if not self.QRKey:
            self.QRKey = uuid.uuid4().hex.upper()  # Tạo UUID, xóa dấu '-' và chuyển sang viết hoa
        super(Restaurant_socket, self).save(*args, **kwargs)
    
class Restaurant_layout(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Tầng 1")  # Mô tả thêm về quán ăn
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    def __str__(self):
        return self.name
    
class Restaurant_space_group(models.Model):
    layout = models.ForeignKey(Restaurant_layout, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Nhóm 1")  # Mô tả thêm về quán ăn
    is_active = models.BooleanField(default=True) # bật
    is_ordering = models.BooleanField(default=False) # đã đặt trước
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    def __str__(self):
        return self.name
class Restaurant_space(models.Model):
    layout = models.ForeignKey(Restaurant_layout, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Vị trí 1")  # Mô tả thêm về quán ăn
    group = models.ForeignKey(Restaurant_space_group, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True) # bật
    is_ordering = models.BooleanField(default=False) # đã đặt trước
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    def __str__(self):
        return self.name
    
class Restaurant_counpon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    is_percent=models.BooleanField(default=True) # giảm theo %
    value=models.IntegerField(default=0) # giảm bao nhiêu
    max_discount=models.IntegerField(default=0) # giảm tối đa bao tiền
    min_of_all_order=models.IntegerField(default=0) # đơn hàng đã đặt đạt bao nhiêu
    min_of_this_order=models.IntegerField(default=0) # đơn hàng này phải đạt bao nhiêu
    max_for_person=models.IntegerField(default=0) # một người được dùng tối đa bao lần
    is_for_first_order=models.BooleanField(default=False) # chỉ cho đơn hàng đầu tiên
    max_use=models.IntegerField(default=0) # lượt dùng tối đa
    start_use = models.DateTimeField(null=True,blank=True)  # Ngày bắt đầu
    end_use = models.DateTimeField(null=True,blank=True)  # Ngày kết thúc
    title = models.CharField(max_length=200,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description_short = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    def __str__(self):
        return self.title
    
class Restaurant_staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    is_Admin = models.BooleanField(default=True)  # Số điện thoại quán ăn
    is_Active = models.BooleanField(default=True)  # Số điện thoại quán ăn
    description = models.TextField(blank=True, null=True)  # Mô tả thêm về quán ăn
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    
    def __str__(self):
        return self.user.username if self.user is not None else None
    
class Restaurant_menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)  # Liên kết với quán ăn
    name = models.CharField(max_length=100)  # Tên memu
    is_online = models.BooleanField(default=True)  # Trạng thái có sẵn hay không
    description = models.TextField(blank=True, null=True)  # Mô tả món ăn
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
class Restaurant_menu_groups(models.Model):
    menu = models.ForeignKey(Restaurant_menu, on_delete=models.CASCADE)  # Liên kết với quán ăn
    name = models.CharField(max_length=100)  # Tên memu
    is_online = models.BooleanField(default=True)  # Trạng thái có sẵn hay không
    description = models.TextField(blank=True, null=True)  # Mô tả món ăn
    
    def __str__(self):
        return f"{self.name}"
    
class Restaurant_menu_marks(models.Model):
    menu = models.ForeignKey(Restaurant_menu, on_delete=models.CASCADE)  # Liên kết với quán ăn
    name = models.CharField(max_length=100)  # Tên memu
    is_online = models.BooleanField(default=True)  # Trạng thái có sẵn hay không
    description = models.TextField(blank=True, null=True)  # Mô tả món ăn
    
    def __str__(self):
        return f"{self.name}"
    
class Restaurant_menu_items(models.Model):
    menu = models.ForeignKey(Restaurant_menu, on_delete=models.CASCADE)  # Liên kết với quán ăn
    mark = models.ManyToManyField(Restaurant_menu_marks, blank=True)  # Liên kết với quán ăn
    group = models.ManyToManyField(Restaurant_menu_groups, blank=True)  # Liên kết với quán ăn
    name = models.CharField(max_length=222,null=True, blank=True)  # Tên memu
    price = models.FloatField(default=0)
    is_hot = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_online = models.BooleanField(default=True)  # Trạng thái có đặt online không
    is_ship = models.BooleanField(default=True)  # Trạng thái có đặt online không
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    image64_mini = models.TextField(null=True, blank=True)
    image64_full = models.TextField(null=True, blank=True)
    image64_sub1 = models.TextField(null=True, blank=True)
    image64_sub2 = models.TextField(null=True, blank=True)
    image64_sub3 = models.TextField(null=True, blank=True)
    short_description = models.TextField(blank=True, null=True)  # Mô tả món ăn
    description = models.TextField(blank=True, null=True)  # Mô tả món ăn
    def __str__(self):
        return f"{self.name} - {self.price}"
    class Meta:
        ordering = ['-id']
        
class Restaurant_order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('CREATED', 'Đã tạo'),
        ('RECEIVED', 'Đã nhận'),
        ('SHIPPING', 'Đang ship'),
        ('DELIVERED', 'Đã giao'),
    ]
    OrderKey = models.CharField(max_length=32, unique=True, editable=False, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)
    user_order = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='CREATED')
    is_use_coupon = models.BooleanField(default=True)  # Trạng thái có sẵn hay không
    is_takeaway = models.BooleanField(default=True)  # Mang về
    is_online = models.BooleanField(default=True)  # Đơn online
    is_paid = models.BooleanField(default=True)  # Thanh toán
    is_paided = models.BooleanField(default=True)  # Xác nhận thanh toán
    
    def __str__(self):
        return f"{self.OrderKey} - {self.is_paid} - {self.is_paided}"
    def save(self, *args, **kwargs):
        if not self.OrderKey:
            self.OrderKey = uuid.uuid4().hex.upper()
        super(Restaurant_order, self).save(*args, **kwargs)
        
class Restaurant_order_items(models.Model):
    Order = models.ForeignKey(Restaurant_order, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ForeignKey(Restaurant_menu_items, on_delete=models.CASCADE)  # Liên kết với quán ăn
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.Order.OrderKey}_{self.items.name}"
    
class Restaurant_counpon_history(models.Model):
    Order = models.ForeignKey(Restaurant_order, on_delete=models.SET_NULL, null=True, blank=True)
    counpon = models.ForeignKey(Restaurant_counpon, on_delete=models.SET_NULL, null=True, blank=True) # mã giảm
    counpon_count = models.IntegerField(default=0) # bộ đếm
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # người dùng
    discount=models.IntegerField(default=0) # giảm thực tế
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật
    def __str__(self):
        return f"{self.Order.OrderKey}_{self.items.name}"
    
    def save(self, *args, **kwargs):
        # Nếu đây là một bản ghi mới
        if not self.pk:
            if self.counpon:
                self.counpon_count = Restaurant_counpon_history.objects.filter(counpon=self.counpon).count() + 1
        super(Restaurant_counpon_history, self).save(*args, **kwargs)
        