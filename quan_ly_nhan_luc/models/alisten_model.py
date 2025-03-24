### receiver
# Signal để tạo SubPermission tự động
from django.db.models.signals import post_save
from django.dispatch import receiver
from .permission import *

# Signal để tạo SubPermission tự động
@receiver(post_save, sender=Permission)
def create_sub_permissions(sender, instance, created, **kwargs):
    if created:
        sub_permissions = [
            {'permission_type': 'view', 'description': f'Quyền xem {instance.name.lower()}'},
            {'permission_type': 'edit', 'description': f'Quyền sửa {instance.name.lower()}'},
            {'permission_type': 'delete', 'description': f'Quyền xóa {instance.name.lower()}'},
            {'permission_type': 'update', 'description': f'Quyền cập nhật {instance.name.lower()}'},
            {'permission_type': 'close', 'description': f'Quyền đóng {instance.name.lower()}'},
            {'permission_type': 'open', 'description': f'Quyền mở {instance.name.lower()}'},
            {'permission_type': 'approve', 'description': f'Quyền duyệt {instance.name.lower()}'},
            {'permission_type': 'reject', 'description': f'Quyền từ chối {instance.name.lower()}'},
        ]
        for sub_perm in sub_permissions:
            SubPermission.objects.create(
                permission=instance,
                permission_type=sub_perm['permission_type'],
                description=sub_perm['description']
            )