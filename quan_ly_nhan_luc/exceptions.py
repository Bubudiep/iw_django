# quan_ly_nhan_luc/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

class ValidationErrorCustom(ValidationError):
    def __init__(self, detail=None, code=None, custom_code=None):
        # Gọi constructor của ValidationError
        super().__init__(detail, code)
        self.custom_code = custom_code  # Mã lỗi tùy chỉnh

    def __str__(self):
        # Trả về lỗi dưới dạng chuỗi thay vì danh sách
        return f"Error {self.custom_code}: {self.detail}" if self.custom_code else str(self.detail)
    
def custom_exception_handler(exc, context):
    # Gọi exception handler mặc định của Django REST framework
    response = exception_handler(exc, context)

    # Nếu lỗi là ValidationErrorCustom, sửa đổi lỗi trả về
    if isinstance(exc, ValidationErrorCustom):
        response.data = {
            "Error": str(exc),  # Lỗi mô tả
            "CustomCode": exc.custom_code  # Mã lỗi tùy chỉnh
        }

    # Nếu lỗi là một ValidationError (ví dụ: lỗi do trường hợp không hợp lệ)
    elif isinstance(exc, ValidationError):
        # Sửa đổi lỗi trả về thành dạng JSON chuẩn
        response.data = {
            "Error": exc.detail[0] if isinstance(exc.detail, list) else str(exc.detail),
            "CustomCode": "invalid"  # Bạn có thể thêm mã lỗi tùy chỉnh ở đây
        }

    return response