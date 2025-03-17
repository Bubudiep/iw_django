from .a import *
from .company import *

class Ngaycong(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE,
                                 null=True,blank=True)
    work_date = models.DateField(null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        
class Bangcong(models.Model):
    STATUS_CHOICES = [
        ('create', 'Tạo mới'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    
    company = models.ForeignKey(company, on_delete=models.CASCADE, null=True, blank=True)
    uploader = models.ForeignKey(company_staff, on_delete=models.SET_NULL, null=True, blank=True, related_name="bangcong_uploader")
    operator = models.ForeignKey(company_operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="bangcong_operator")
    work_date = models.ForeignKey(Ngaycong, on_delete=models.SET_NULL, null=True, blank=True, related_name="bangcong_workdate")
    
    check_in = models.TimeField(null=True, blank=True, verbose_name="Giờ vào")
    check_out = models.TimeField(null=True, blank=True, verbose_name="Giờ ra")
    overtime_hours = models.FloatField(default=0.0, verbose_name="Giờ tăng ca")  # Giờ tăng ca (đơn vị: giờ)
    total_work_hours = models.FloatField(default=0.0, verbose_name="Số giờ làm việc")  # Tổng số giờ làm việc
    salary_coefficient = models.FloatField(default=1.0, verbose_name="Hệ số lương")  # Hệ số lương
    
    comment = models.TextField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    nhacungcap = models.ForeignKey(company_vendor, on_delete=models.SET_NULL, null=True, blank=True)
    congty = models.ForeignKey(company_customer, on_delete=models.SET_NULL, null=True, blank=True)
    nhachinh = models.ForeignKey(company_supplier, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Nếu chưa có work_date, tạo mới hoặc lấy ngày công tương ứng
        if self.id:  # Chỉ lưu lịch sử nếu đây không phải là bản ghi mới
            old_instance = Bangcong.objects.get(id=self.id)
            if (
                old_instance.check_in != self.check_in or
                old_instance.check_out != self.check_out or
                old_instance.overtime_hours != self.overtime_hours or
                old_instance.total_work_hours != self.total_work_hours or
                old_instance.salary_coefficient != self.salary_coefficient
            ):
                BangCongHistory.objects.create(
                    bangcong=self,
                    updated_by=self.operator,  # Người sửa là operator
                    old_check_in=old_instance.check_in,
                    old_check_out=old_instance.check_out,
                    old_overtime_hours=old_instance.overtime_hours,
                    old_total_work_hours=old_instance.total_work_hours,
                    old_salary_coefficient=old_instance.salary_coefficient,
                    new_check_in=self.check_in,
                    new_check_out=self.check_out,
                    new_overtime_hours=self.overtime_hours,
                    new_total_work_hours=self.total_work_hours,
                    new_salary_coefficient=self.salary_coefficient,
                )

        if not self.work_date:
            ngay_hien_tai = now().date()
            ngaycong, created = Ngaycong.objects.get_or_create(
                work_date=ngay_hien_tai,
                company=self.company,  
                defaults={'comment': 'Tự động tạo'}
            )
            self.work_date = ngaycong
        
        # Tính tổng số giờ làm việc (nếu có check_in và check_out)
        if self.check_in and self.check_out:
            fmt = "%H:%M:%S"
            check_in_time = datetime.strptime(str(self.check_in), fmt)
            check_out_time = datetime.strptime(str(self.check_out), fmt)
            work_duration = (check_out_time - check_in_time).total_seconds() / 3600  # Chuyển thành giờ
            
            # Tính tổng giờ làm việc
            self.total_work_hours = work_duration + self.overtime_hours
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.get_status_display()}"
      
class YeuCauSuaBangCong(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    bangcong = models.ForeignKey(Bangcong, on_delete=models.CASCADE, related_name="yeucau_sua")
    staff_sender = models.ForeignKey(company_staff, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="yeucau_nhanvien")
    operator_sender = models.ForeignKey(company_operator, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="yeucau_congnhan")
    ly_do = models.TextField("Lý do sửa", max_length=500)
    trang_thai = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    staff_sender = models.ForeignKey(company_staff, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="yeucau_quanly")
    ngay_duyet = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def approve(self, user):
        self.trang_thai = 'approved'
        self.nguoi_duyet = user
        self.ngay_duyet = datetime.now()
        self.save()
    def reject(self, user):
        self.trang_thai = 'rejected'
        self.nguoi_duyet = user
        self.ngay_duyet = datetime.now()
        self.save()
    def __str__(self):
        return f"Yêu cầu {self.id} - {self.bangcong.id} ({self.get_trang_thai_display()})"
      
class BangCongHistory(models.Model):
    bangcong = models.ForeignKey(Bangcong, on_delete=models.CASCADE, related_name="history")
    yeucau = models.ForeignKey(YeuCauSuaBangCong, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Yêu cầu sửa")
    old_check_in = models.TimeField(null=True, blank=True, verbose_name="Giờ vào cũ")
    old_check_out = models.TimeField(null=True, blank=True, verbose_name="Giờ ra cũ")
    old_overtime_hours = models.FloatField(null=True, blank=True, verbose_name="Giờ tăng ca cũ")
    old_total_work_hours = models.FloatField(null=True, blank=True, verbose_name="Số giờ làm việc cũ")
    old_salary_coefficient = models.FloatField(null=True, blank=True, verbose_name="Hệ số lương cũ")

    new_check_in = models.TimeField(null=True, blank=True, verbose_name="Giờ vào mới")
    new_check_out = models.TimeField(null=True, blank=True, verbose_name="Giờ ra mới")
    new_overtime_hours = models.FloatField(null=True, blank=True, verbose_name="Giờ tăng ca mới")
    new_total_work_hours = models.FloatField(null=True, blank=True, verbose_name="Số giờ làm việc mới")
    new_salary_coefficient = models.FloatField(null=True, blank=True, verbose_name="Hệ số lương mới")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Lịch sử {self.id} - Bảng công {self.bangcong.id} - {self.updated_at}"
        