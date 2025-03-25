from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import config
from ..core.auth import verify_auth_cookie, is_path_protected


class SwagGuardMiddleware(BaseHTTPMiddleware):
    """
    Swagger 문서 및 관련 경로에 대한 접근을 제한하는 FastAPI 미들웨어
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        
        # 경로가 보호 대상인지 확인
        if is_path_protected(path):
            # 쿠키 이름 가져오기
            cookie_name = config.get("cookie_name", "swaguard_auth")
            
            # 로그인 페이지는 예외 처리
            login_path = config.get("login_path", "/swaguard/login")
            if path == login_path:
                return await call_next(request)
            
            # 쿠키 가져오기
            cookie = request.cookies.get(cookie_name)
            
            # 쿠키가 없거나 유효하지 않으면 로그인 페이지로 리다이렉트
            if not cookie or not verify_auth_cookie(cookie):
                # API 응답이면 401 상태 코드 반환
                if path.endswith(".json") or request.headers.get("accept") == "application/json":
                    return Response(
                        content='{"detail":"Unauthorized: Authentication required"}',
                        status_code=401,
                        media_type="application/json"
                    )
                
                # HTML 응답이면 로그인 페이지로 리다이렉트
                redirect_url = login_path
                if "?" not in redirect_url:
                    redirect_url += f"?next={path}"
                
                return Response(
                    status_code=307,  # Temporary Redirect
                    headers={"Location": redirect_url}
                )
        
        # 인증 성공 또는 보호 대상이 아닌 경로인 경우 요청 진행
        return await call_next(request)
