from .a import *
from .company import *

class AdvanceType(models.Model): # loại phê duyệt
    typecode = models.CharField(max_length=100, unique=True)
    need_operator = models.BooleanField(default=False) # người thụ hưởng là công nhân
    need_approver = models.BooleanField(default=False) # cần phê duyệt
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(company, on_delete=models.CASCADE,
                                 null=True,blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.id}"
    
class AdvanceReasonType(models.Model): # phân loại nguyên nhân phê duyệt
    company = models.ForeignKey(company, on_delete=models.CASCADE, null=True,blank=True)
    typename = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.id}"
      
class AdvanceRequest(models.Model): # phê duyệt
    STATUS_CHOICES = [
        ('cancel', 'Hủy bỏ'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    PAYMENT_CHOICES = [
        ('unpaid', 'Chưa thanh toán'),
        ('paid', 'Đã thanh toán'),
    ]
    RETRIEVE_CHOICES = [
        ('not_retrieved', 'Chưa thu hồi'),
        ('retrieved', 'Đã thu hồi'),
    ]
    company = models.ForeignKey(company, on_delete=models.CASCADE,
                                 null=True,blank=True)
    # người yêu cầu
    requester = models.ForeignKey(company_staff, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_requests")
    requesttype = models.ForeignKey(AdvanceType, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_type")
    # người phê duyệt
    approver = models.ForeignKey(company_staff, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_approver")
    # người thụ hưởng
    operator = models.ForeignKey(company_operator, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_operator")
    # số tiền
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # lý do
    reason = models.ForeignKey(AdvanceReasonType, on_delete=models.SET_NULL,
                               null=True,blank=True, related_name="advance_reason")
    request_date = models.DateField(null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='unpaid')
    retrieve_status = models.CharField(max_length=15, choices=RETRIEVE_CHOICES, default='not_retrieved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.amount} - {self.get_status_display()}"   
    
class AdvanceRequestHistory(models.Model): # phân loại nguyên nhân phê duyệt
    ACTION_CHOICES = [
        ('update', 'Cập nhập'),
        ('edit', 'Chỉnh sửa'),
        ('create', 'Tạo mới'),
        ('cancel', 'Hủy bỏ'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    request = models.ForeignKey(AdvanceRequest, on_delete=models.CASCADE, null=True,blank=True)
    user = models.ForeignKey(company_staff, on_delete=models.SET_NULL,
                                 null=True,blank=True, 
                                 related_name="advance_history_approver")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default='pending')
    old_data = models.JSONField(null=True,blank=True)
    new_data = models.JSONField(null=True,blank=True)
    comment = models.TextField(null=True,blank=True,max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.id}"
      