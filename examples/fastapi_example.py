import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

# 라이브러리 경로를 추가하여 직접 import할 수 있게 합니다
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# SwagGuard 라이브러리 import
import swaguard
from swaguard import SwagGuardMiddleware, create_login_router, verify_swagger_cookie, config, create_user


# 커스텀 설정 적용
config.set("cookie_name", "custom_auth_cookie")
config.set("cookie_expire_minutes", 30)  # 30분으로 설정
config.set("login_path", "/custom/login")  # 커스텀 로그인 경로
config.set("logout_path", "/custom/logout")  # 커스텀 로그아웃 경로
config.add_protected_path("/api/protected")  # 보호할 추가 경로

# 테스트용 사용자 생성
create_user("admin", "password")
print("Credentials: admin / password")
print(f"Custom login path: {config.get('login_path')}")
print(f"Custom logout path: {config.get('logout_path')}")
print(f"Protected paths: {config.get('protected_paths')}")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="SwagGuard Example",
    description="SwagGuard를 사용한 FastAPI 예제 애플리케이션입니다.",
    version="0.1.0",
)

# SwagGuard 미들웨어 등록
app.add_middleware(SwagGuardMiddleware)

# SwagGuard 로그인 라우터 등록
login_router = create_login_router()
app.include_router(login_router, tags=["authentication"])


# 테스트용 API 엔드포인트
@app.get("/", tags=["example"])
async def root():
    """애플리케이션 루트 페이지"""
    return {"message": "Welcome to SwagGuard Example Application"}

@app.get("/config", tags=["example"])
async def show_config():
    """현재 SwagGuard 설정을 보여주는 엔드포인트"""
    return {
        "cookie_name": config.get("cookie_name"),
        "cookie_expire_minutes": config.get("cookie_expire_minutes"),
        "login_path": config.get("login_path"),
        "logout_path": config.get("logout_path"),
        "protected_paths": config.get("protected_paths")
    }

@app.get("/api/public", tags=["example"])
async def public_endpoint():
    """이 엔드포인트는 공개적으로 접근할 수 있습니다."""
    return {"message": "This is a public endpoint"}


@app.get("/api/protected", tags=["example"])
async def protected_endpoint(username: str = Depends(verify_swagger_cookie)):
    """이 엔드포인트는 SwagGuard로 보호되어 있습니다."""
    return {"message": f"Hello, {username}! This is a protected endpoint."}


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    """HTTP 예외를 처리하는 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(
        "fastapi_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
