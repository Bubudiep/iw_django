from .a import *
class IntegrityErrorLog(models.Model):
    models_name = models.CharField(max_length=255, blank=True, null=True)
    api_name = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField()  # Lưu thông báo lỗi
    timestamp = models.DateTimeField(default=timezone.now)  # Lưu thời gian xảy ra lỗi
    endpoint = models.CharField(max_length=255, blank=True, null=True)  # Endpoint liên quan
    payload = models.JSONField(blank=True, null=True)  # Lưu dữ liệu gửi lên gây ra lỗi
    class Meta:
        ordering = ['-id']  # Sắp xếp theo thời gian bắt đầu mới nhất
        verbose_name = "API Errors"
        verbose_name_plural = "API Errors"
    def __str__(self):
        return f"Error at {self.endpoint} on {self.timestamp}"
  