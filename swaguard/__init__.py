"""
SwagGuard - Swagger/OpenAPI UI 보호 라이브러리

이 라이브러리는 FastAPI 및 Django 애플리케이션에서 Swagger/OpenAPI UI를 보호하기 위한 기능을 제공합니다.
인증된 사용자만 Swagger 문서에 접근할 수 있도록 보호하는 기능을 제공합니다.
"""

__version__ = "0.1.0"

# FastAPI 관련 기능
from .decorators.fastapi import swagger_protect, verify_swagger_cookie
from .middlewares.fastapi_mw import SwagGuardMiddleware
from .routes.login_route import create_login_router

# 설정 관련 기능
from .config import config

# 유틸리티 기능
from .utils.helper import create_user, setup_initial_users

# 보안 관련 기능
from .core.security import hash_password, verify_password

# 기본 초기화 수행
setup_initial_users()