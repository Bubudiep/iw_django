from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import random
import string

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID cho công ty
    name = models.CharField(max_length=255)
    startday = models.IntegerField(default=1)
    address = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name
      
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.user:
            newuser = User.objects.create_user(username=f"EMP_{self.company.id}_{self.username}",
                                            password=''.join(random.choices(string.ascii_letters 
                                                                    + string.digits, k=12)))
            self.user=newuser
        if not self.username or not self.password:
            raise ValidationError("Username và password không được để trống.")
        if not self.password.startswith('pbkdf2_sha256$'):  # Kiểm tra xem mật khẩu đã mã hóa chưa
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('company', 'username')
    def __str__(self):
        return f"{self.username} {self.company.name}"

class Profile(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    emp_id = models.CharField(max_length=12, null=True, blank=True)
    avatar = models.TimeField(null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    deparment = models.CharField(max_length=200, null=True, blank=True)
    
    zalo_id= models.CharField(max_length=200, null=True, blank=True)
    zalo_number = models.CharField(max_length=200, null=True, blank=True)
    
    join_date = models.DateField(null=True, blank=True)
    leave_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username}_{self.full_name}"

class Punchtime(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    emp_id = models.CharField(max_length=20, null=True, blank=True)
    punch_time = models.DateTimeField(null=True, blank=True)
    att_date = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user} - {self.att_date} - {self.punch_time}"
      
class Attendance(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    record_id = models.CharField(max_length=50, null=True, blank=True)
    emp_id = models.CharField(max_length=20, null=True, blank=True)
    week = models.IntegerField(null=True, blank=True)
    weekday = models.IntegerField(null=True, blank=True)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    punch_time = models.ManyToManyField(Punchtime)
    att_date = models.DateField()
    is_check = models.BooleanField(default=False)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.att_date}"
      
class AttendanceTicket(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="att_req_user")
    implement = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="att_imp_user")
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200, null=True, blank=True)
    is_check = models.BooleanField(default=False)
    is_close = models.BooleanField(default=False)
    is_accept = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} {self.attendance.id}"

class AttendanceTicketComment(models.Model):
    ticket = models.ForeignKey(AttendanceTicket, on_delete=models.CASCADE)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.comment}"
      
class EmployeeMessage(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="em_req_user")
    implement = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="em_imp_user")
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_check = models.BooleanField(default=False)
    is_close = models.BooleanField(default=False)
    is_accept = models.BooleanField(default=False)
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(max_length=500, null=True, blank=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.title} - {self.user.username}"
      
class EmployeeMessageComment(models.Model):
    message = models.ForeignKey(EmployeeMessage, on_delete=models.CASCADE)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.comment}"
      