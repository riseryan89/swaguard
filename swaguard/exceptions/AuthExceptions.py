class SwagGuardException(Exception):
    """SwagGuard 라이브러리의 기본 예외 클래스"""
    pass


class AuthenticationError(SwagGuardException):
    """인증 오류 발생 시 사용하는 예외 클래스"""
    def __init__(self, message="Authentication failed", status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ConfigurationError(SwagGuardException):
    """설정 오류 발생 시 사용하는 예외 클래스"""
    def __init__(self, message="Configuration error"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(AuthenticationError):
    """사용자를 찾을 수 없을 때 사용하는 예외 클래스"""
    def __init__(self, username=""):
        message = f"User {'not found' if not username else username + ' not found'}"
        super().__init__(message=message, status_code=401)


class InvalidCredentialsError(AuthenticationError):
    """자격 증명이 잘못되었을 때 사용하는 예외 클래스"""
    def __init__(self):
        super().__init__(message="Invalid credentials", status_code=401)


class UnauthorizedAccessError(AuthenticationError):
    """인증되지 않은 접근 시 사용하는 예외 클래스"""
    def __init__(self):
        super().__init__(message="Unauthorized access", status_code=401)
