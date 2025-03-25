# SwagGuard

SwagGuard는 Django와 FastAPI 애플리케이션에서 Swagger/OpenAPI UI를 보호하기 위한 Python 라이브러리입니다. 인증된 사용자만 API 문서에 접근할 수 있도록 합니다.

## 특징

- Swagger UI(/docs), ReDoc(/redoc) 및 OpenAPI 스키마(/openapi.json) 엔드포인트 보호
- 간단한 HTTP-only 쿠키 기반 인증
- 설정 가능한 쿠키 만료 시간 (기본 60분)
- 환경 변수 또는 YAML 파일을 통한 설정
- FastAPI 애플리케이션 지원 (현재 구현)
- Django 애플리케이션 지원 (향후 구현 예정)

## 설치

```bash
pip install swaguard
```

또는 소스에서 직접 설치:

```bash
git clone https://github.com/username/swaguard.git
cd swaguard
pip install -e .
```

## 사용 방법

### FastAPI에서 사용하기

1. 미들웨어를 사용하여 모든 Swagger 관련 경로 보호:

```python
from fastapi import FastAPI
from swaguard import SwagGuardMiddleware, create_login_router, create_user

# 사용자 생성
create_user("admin", "password")

app = FastAPI()

# SwagGuard 미들웨어 등록
app.add_middleware(SwagGuardMiddleware)

# 로그인 라우터 등록
login_router = create_login_router()
app.include_router(login_router)
```

2. 종속성 주입을 사용하여 특정 엔드포인트 보호:

```python
from fastapi import FastAPI, Depends
from swaguard import verify_swagger_cookie

app = FastAPI()

@app.get("/api/protected")
async def protected_endpoint(username: str = Depends(verify_swagger_cookie)):
    return {"message": f"Hello, {username}!"}
```

## 설정

SwagGuard는 다음과 같은 방법으로 설정할 수 있습니다:

### 환경 변수

```bash
# 쿠키 설정
export SWAGUARD_COOKIE_NAME="swaguard_auth"
export SWAGUARD_COOKIE_EXPIRE_MINUTES="60"
export SWAGUARD_COOKIE_SECURE="true"
export SWAGUARD_COOKIE_HTTPONLY="true"
export SWAGUARD_COOKIE_SAMESITE="lax"

# 경로 설정
export SWAGUARD_LOGIN_PATH="/swaguard/login"
export SWAGUARD_LOGOUT_PATH="/swaguard/logout"

# 사용자 설정 (개발 환경에서만 사용 권장)
export SWAGUARD_USERS="admin:password,user:userpass"

# 비밀 키 설정
export SWAGUARD_SECRET_KEY="your-secret-key"
```

### YAML 설정 파일

```yaml
# swaguard_config.yaml
cookie_name: swaguard_auth
cookie_expire_minutes: 60
cookie_secure: true
cookie_httponly: true
cookie_samesite: lax
login_path: /swaguard/login
logout_path: /swaguard/logout
protected_paths:
  - /docs
  - /redoc
  - /openapi.json
users:
  admin: $2b$12$...  # 해시된 비밀번호
```

## 예제

예제 폴더에 샘플 애플리케이션이 포함되어 있습니다:

- `examples/fastapi_example.py`: FastAPI를 사용한 예제

예제 실행:

```bash
cd examples
python fastapi_example.py
```

그런 다음 브라우저에서 http://localhost:8000/docs 에 접속하면 로그인 페이지로 리다이렉트됩니다.

## 라이선스

MIT

## 기여하기

Pull Request 및 이슈 제출을 환영합니다. 주요 변경 사항에 대해서는 먼저 이슈를 통해 논의해 주세요.
