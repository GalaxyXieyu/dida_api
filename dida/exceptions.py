"""
滴答清单 SDK 异常类定义
"""

class DidaException(Exception):
    """滴答清单SDK基础异常类"""
    pass

class AuthenticationError(DidaException):
    """认证相关错误"""
    pass

class APIError(DidaException):
    """API调用错误"""
    def __init__(self, message: str, status_code: int, response: dict):
        self.status_code = status_code
        self.response = response
        super().__init__(f"{message} (Status: {status_code})")

class ValidationError(DidaException):
    """数据验证错误"""
    pass

class ConfigurationError(DidaException):
    """配置相关错误"""
    pass 