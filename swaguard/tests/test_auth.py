import pytest
import time
from unittest.mock import patch, MagicMock

from swaguard.core.auth import authenticate_user, create_auth_cookie, verify_auth_cookie
from swaguard.core.security import hash_password
from swaguard.config import config


@pytest.fixture
def setup_test_user():
    # 테스트 사용자 설정
    test_username = "testuser"
    test_password = "testpassword"
    test_password_hash = hash_password(test_password)
    
    # 설정에 테스트 사용자 추가
    config.add_user(test_username, test_password_hash)
    
    yield test_username, test_password
    
    # 테스트 후 사용자 제거
    config.remove_user(test_username)


def test_authenticate_user(setup_test_user):
    username, password = setup_test_user
    
    # 올바른 자격 증명으로 인증
    assert authenticate_user(username, password) is True
    
    # 잘못된 비밀번호로 인증
    assert authenticate_user(username, "wrongpassword") is False
    
    # 존재하지 않는 사용자로 인증
    assert authenticate_user("nonexistentuser", password) is False


def test_create_auth_cookie():
    username = "testuser"
    
    # 쿠키 생성
    cookie_value, cookie_options = create_auth_cookie(username)
    
    # 쿠키 값이 문자열인지 확인
    assert isinstance(cookie_value, str)
    assert len(cookie_value) > 0
    
    # 쿠키 옵션이 딕셔너리인지 확인
    assert isinstance(cookie_options, dict)
    assert "httponly" in cookie_options
    assert "secure" in cookie_options
    assert "samesite" in cookie_options
    assert "max-age" in cookie_options


def test_verify_auth_cookie():
    username = "testuser"
    
    # 쿠키 생성
    cookie_value, _ = create_auth_cookie(username)
    
    # 유효한 쿠키 검증
    verified_username = verify_auth_cookie(cookie_value)
    assert verified_username == username
    
    # 잘못된 쿠키 검증
    assert verify_auth_cookie("invalid.cookie.value") is None
    assert verify_auth_cookie(None) is None
    assert verify_auth_cookie("") is None


def test_expired_cookie():
    username = "testuser"
    
    # 현재 시간과 만료 시간 준비
    now = int(time.time())
    # 만료된 시간 (1시간 전)
    expired_time = now - 3600
    
    # 만료된 쿠키 데이터
    from swaguard.core.auth import SECRET_KEY
    from swaguard.core.security import create_signed_value
    
    expired_data = {
        "sub": username,
        "iat": expired_time - 3600,  # 2시간 전 발급
        "exp": expired_time,         # 1시간 전 만료
    }
    
    # 만료된 쿠키 생성
    expired_cookie = create_signed_value(SECRET_KEY, expired_data)
    
    # 만료된 쿠키 검증
    assert verify_auth_cookie(expired_cookie) is None
