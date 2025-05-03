from functools import wraps
from flask import request, _request_ctx_stack
import flask_jwt_extended
from flask_jwt_extended.view_decorators import _decode_jwt_from_request, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

# Lưu các hàm gốc
original_decode_jwt_from_request = _decode_jwt_from_request
original_verify_jwt_in_request = verify_jwt_in_request

# Tạo các dữ liệu giả lập để trả về thay vì lỗi
DUMMY_JWT_DATA = {}
DUMMY_JWT_HEADER = {}

# Ghi đè hàm verify_jwt_in_request để chỉ kiểm tra JWT cho API
def patched_verify_jwt_in_request(*args, **kwargs):
    try:
        # Nếu là API route, áp dụng JWT normaly
        if request.path.startswith('/api/'):
            return original_verify_jwt_in_request(*args, **kwargs)
        
        # Nếu không phải API route, giả lập JWT để không gây ra lỗi
        # Đặt dữ liệu giả trên ngữ cảnh request để code khác có thể sử dụng
        _request_ctx_stack.top.jwt = DUMMY_JWT_DATA
        _request_ctx_stack.top.jwt_header = DUMMY_JWT_HEADER
        _request_ctx_stack.top.jwt_user = {"loaded_user": None}
        _request_ctx_stack.top.jwt_location = None
        return None
    except Exception as e:
        if not request.path.startswith('/api/'):
            # Nếu không phải API route, bỏ qua lỗi
            _request_ctx_stack.top.jwt = DUMMY_JWT_DATA
            _request_ctx_stack.top.jwt_header = DUMMY_JWT_HEADER
            _request_ctx_stack.top.jwt_user = {"loaded_user": None}
            _request_ctx_stack.top.jwt_location = None
            return None
        raise e

# Ghi đè hàm _decode_jwt_from_request để chỉ áp dụng cho API
def patched_decode_jwt_from_request(*args, **kwargs):
    if request.path.startswith('/api/'):
        return original_decode_jwt_from_request(*args, **kwargs)
    # Nếu không phải API route, trả về dữ liệu giả
    return DUMMY_JWT_DATA, DUMMY_JWT_HEADER, None

# Ghi đè NoAuthorizationError để kiểm soát lỗi 401
original_NoAuthorizationError = NoAuthorizationError
class PatchedNoAuthorizationError(original_NoAuthorizationError):
    def __init__(self, *args, **kwargs):
        # Nếu không phải API route, không báo lỗi
        if not request.path.startswith('/api/'):
            pass  # Không làm gì, để tránh lỗi
        else:
            super().__init__(*args, **kwargs)

# Hàm để áp dụng toàn bộ các patch
def apply_jwt_patch():
    # Ghi đè các hàm trong flask_jwt_extended
    flask_jwt_extended.view_decorators._decode_jwt_from_request = patched_decode_jwt_from_request
    flask_jwt_extended.view_decorators.verify_jwt_in_request = patched_verify_jwt_in_request
    flask_jwt_extended.exceptions.NoAuthorizationError = PatchedNoAuthorizationError

    # Đặt một hook để xử lý yêu cầu JWT với mọi route không phải API
    @flask_jwt_extended.jwt_required
    def dummy_jwt_required(*args, **kwargs):
        pass
    
    # Patch decorator jwt_required để bỏ qua nó cho các route không phải API
    original_jwt_required = flask_jwt_extended.jwt_required
    @wraps(original_jwt_required)
    def patched_jwt_required(*args, **kwargs):
        def wrapper(fn):
            @wraps(fn)
            def decorator(*fn_args, **fn_kwargs):
                # Nếu không phải API route, không yêu cầu JWT
                if not request.path.startswith('/api/'):
                    return fn(*fn_args, **fn_kwargs)
                # Nếu là API, áp dụng JWT bình thường
                return original_jwt_required(*args, **kwargs)(fn)(*fn_args, **fn_kwargs)
            return decorator
        return wrapper
    
    # Áp dụng patch cho jwt_required
    flask_jwt_extended.jwt_required = patched_jwt_required