import bcrypt
import time
import base64
import hashlib
import hmac
import json
from typing import Dict, Optional, Tuple, Any


def hash_password(password: str) -> str:
    """
    비밀번호를 해시하여 저장할 수 있는 형태로 변환합니다.
    
    Args:
        password: 해시할 비밀번호 문자열
        
    Returns:
        해시된 비밀번호 문자열
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 텍스트 비밀번호가 해시된 비밀번호와 일치하는지 확인합니다.
    
    Args:
        plain_password: 확인할 일반 텍스트 비밀번호
        hashed_password: 비교할 해시된 비밀번호
        
    Returns:
        비밀번호가 일치하면 True, 그렇지 않으면 False
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_signed_value(secret_key: str, data: Dict[str, Any]) -> str:
    """
    데이터를 JSON으로 직렬화하고 서명하여 쿠키 값을 생성합니다.
    
    Args:
        secret_key: 서명에 사용할 비밀 키
        data: 직렬화할 데이터 딕셔너리
        
    Returns:
        서명된 데이터 문자열
    """
    # 데이터를 JSON 문자열로 변환
    json_data = json.dumps(data)
    
    # Base64로 인코딩
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    
    # HMAC 서명 생성
    signature = hmac.new(
        secret_key.encode('utf-8'),
        encoded_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # 인코딩된 데이터와 서명을 결합
    return f"{encoded_data}.{signature}"


def verify_signed_value(secret_key: str, signed_value: str) -> Optional[Dict[str, Any]]:
    """
    서명된 값을 검증하고 원래 데이터를 반환합니다.
    
    Args:
        secret_key: 서명에 사용된 비밀 키
        signed_value: 서명된 데이터 문자열
        
    Returns:
        성공적으로 검증되면 원래 데이터 딕셔너리, 그렇지 않으면 None
    """
    try:
        # 데이터와 서명 분리
        parts = signed_value.split('.')
        if len(parts) != 2:
            return None
            
        encoded_data, signature = parts
        
        # 서명 검증
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            encoded_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
            
        # 데이터 디코딩
        json_data = base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
        data = json.loads(json_data)
        
        # 만료 시간 확인
        if 'exp' in data and data['exp'] < time.time():
            return None
            
        return data
    except Exception:
        return None


def generate_secret_key() -> str:
    """
    랜덤 비밀 키를 생성합니다.
    
    Returns:
        랜덤 비밀 키 문자열
    """
    random_bytes = bcrypt.gensalt(12)
    return base64.b64encode(random_bytes).decode('utf-8')
