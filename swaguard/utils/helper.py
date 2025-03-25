import os
import secrets
from typing import Dict, List, Any, Optional

from ..config import config
from ..core.security import hash_password


def generate_random_key(length: int = 32) -> str:
    """
    주어진 길이의 랜덤 키를 생성합니다.
    
    Args:
        length: 생성할 키의 길이 (바이트 단위)
        
    Returns:
        랜덤 키 문자열
    """
    return secrets.token_urlsafe(length)


def create_user(username: str, password: str) -> None:
    """
    새 사용자를 생성하고 설정에 추가합니다.
    
    Args:
        username: 사용자 이름
        password: 비밀번호
    """
    # 비밀번호 해시
    password_hash = hash_password(password)
    
    # 사용자 추가
    config.add_user(username, password_hash)


def load_users_from_env() -> None:
    """
    환경 변수에서 사용자 정보를 로드합니다.
    
    환경 변수 형식:
    SWAGUARD_USERS=username1:password1,username2:password2
    """
    users_str = os.environ.get("SWAGUARD_USERS", "")
    if not users_str:
        return
        
    try:
        # 쉼표로 구분된 사용자 목록 파싱
        user_pairs = users_str.split(",")
        for pair in user_pairs:
            if ":" not in pair:
                continue
                
            username, password = pair.split(":", 1)
            create_user(username.strip(), password.strip())
    except Exception as e:
        print(f"사용자 로드 중 오류 발생: {e}")


def setup_initial_users() -> None:
    """
    초기 사용자 설정을 수행합니다.
    환경 변수, 설정 파일 또는 기본값에서 사용자를 로드합니다.
    """
    # 환경 변수에서 사용자 로드
    load_users_from_env()
    
    # 설정 파일에서 사용자 로드는 config.py에서 이미 처리
    
    # 사용자가 없으면 기본 사용자 설정
    users = config.get_users()
    if not users:
        print("Warning: No users found. Creating default 'admin' user with a random password.")
        admin_password = generate_random_key(16)
        create_user("admin", admin_password)
        print(f"Default credentials: admin / {admin_password}")
        print("Please change this password as soon as possible.")


def get_protected_paths() -> List[str]:
    """
    보호된 경로 목록을 가져옵니다.
    
    Returns:
        보호된 경로 목록
    """
    return config.get("protected_paths", [])
