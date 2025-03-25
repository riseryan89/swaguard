from typing import Callable, Optional, List
from functools import wraps

from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyCookie

from ..config import config
from ..core.auth import verify_auth_cookie, is_path_protected


def get_cookie_name() -> str:
    """인증 쿠키 이름을 가져옵니다."""
    return config.get("cookie_name", "swaguard_auth")


# 쿠키 기반 인증을 위한 의존성
cookie_scheme = APIKeyCookie(name=get_cookie_name())


async def verify_swagger_cookie(
    request: Request, 
    cookie: Optional[str] = Depends(cookie_scheme)
) -> str:
    """
    Swagger UI 및 관련 경로에 대한 접근 권한을 확인합니다.
    
    Args:
        request: FastAPI Request 객체
        cookie: 요청에서 추출한 쿠키 값
        
    Returns:
        인증된 사용자 이름
        
    Raises:
        HTTPException: 인증 실패 시 발생
    """
    path = request.url.path
    
    # 요청 경로가 보호되어야 하는지 확인
    if not is_path_protected(path):
        return ""  # 보호되지 않은 경로는 인증 검사 건너뜀
    
    # 쿠키가 없으면 401 반환
    if not cookie:
        raise HTTPException(status_code=401, detail="Unauthorized: Authentication required")
    
    # 쿠키 검증
    username = verify_auth_cookie(cookie)
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token")
    
    return username


def swagger_protect(paths: Optional[List[str]] = None):
    """
    Swagger UI 및 관련 경로를 보호하는 데코레이터
    
    Args:
        paths: 보호할 추가 경로 목록 (기본값 외에 추가로 보호할 경로)
        
    Example:
        @app.get("/docs")
        @swagger_protect()
        async def get_swagger_ui():
            ...
    """
    # 경로 목록이 제공되면 보호 대상 경로에 추가
    if paths:
        for path in paths:
            config.add_protected_path(path)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # FastAPI의 Request 객체를 찾아 인증 수행
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request and 'request' in kwargs:
                request = kwargs['request']
            
            if not request:
                raise ValueError("Request object not found in function arguments")
            
            # 쿠키 검증
            cookie_name = get_cookie_name()
            cookie = request.cookies.get(cookie_name)
            
            if not cookie:
                raise HTTPException(status_code=401, detail="Unauthorized: Authentication required")
            
            username = verify_auth_cookie(cookie)
            if not username:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token")
            
            # 인증 성공 시 원래 함수 실행
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
