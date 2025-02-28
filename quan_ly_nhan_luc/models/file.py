from .a import *
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
    