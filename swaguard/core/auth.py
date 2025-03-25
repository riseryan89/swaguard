import time
import os
from typing import Dict, Optional, Tuple

from ..config import config
from .security import verify_password, create_signed_value, verify_signed_value


# 기본적으로 환경 변수나 설정 파일에서 가져오지 않았다면 랜덤 시크릿 키 생성
SECRET_KEY = os.environ.get("SWAGUARD_SECRET_KEY", "")
if not SECRET_KEY:
    from .security import generate_secret_key
    SECRET_KEY = generate_secret_key()


def authenticate_user(username: str, password: str) -> bool:
    """
    사용자를 인증합니다.
    
    Args:
        username: 사용자 이름
        password: 비밀번호
        
    Returns:
        인증 성공 시 True, 실패 시 False
    """
    users = config.get_users()
    if username not in users:
        return False
        
    stored_password_hash = users[username]
    return verify_password(password, stored_password_hash)


def create_auth_cookie(username: str) -> Tuple[str, Dict[str, str]]:
    """
    인증 쿠키를 생성합니다.
    
    Args:
        username: 인증된 사용자 이름
        
    Returns:
        (쿠키 값, 쿠키 설정 옵션) 튜플
    """
    # 현재 시간과 만료 시간 계산
    now = int(time.time())
    expires = now + (config.get("cookie_expire_minutes", 60) * 60)
    
    # 쿠키 데이터 생성
    cookie_data = {
        "sub": username,  # subject (사용자)
        "iat": now,       # issued at (발급 시간)
        "exp": expires,   # expiration (만료 시간)
    }
    
    # 서명된 쿠키 값 생성
    cookie_value = create_signed_value(SECRET_KEY, cookie_data)
    
    # 쿠키 설정 옵션
    cookie_options = {
        "httponly": str(config.get("cookie_httponly", True)).lower(),
        "secure": str(config.get("cookie_secure", True)).lower(),
        "samesite": config.get("cookie_samesite", "lax"),
        "path": "/",
        "max-age": str(config.get("cookie_expire_minutes", 60) * 60),
    }
    
    return cookie_value, cookie_options


def verify_auth_cookie(cookie_value: Optional[str]) -> Optional[str]:
    """
    인증 쿠키를 확인합니다.
    
    Args:
        cookie_value: 쿠키 값 문자열
        
    Returns:
        쿠키가 유효하면 사용자 이름, 그렇지 않으면 None
    """
    if not cookie_value:
        return None
        
    data = verify_signed_value(SECRET_KEY, cookie_value)
    if not data:
        return None
        
    # 쿠키에서 사용자 이름 추출
    return data.get("sub")


def is_path_protected(path: str) -> bool:
    """
    주어진 경로가 보호되어야 하는지 확인합니다.
    
    Args:
        path: 확인할 경로
        
    Returns:
        경로가 보호되어야 하면 True, 그렇지 않으면 False
    """
    protected_paths = config.get("protected_paths", [])
    return any(path.startswith(protected) for protected in protected_paths)
