from typing import Optional
from fastapi import APIRouter, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from ..config import config
from ..core.auth import authenticate_user, create_auth_cookie


class LoginForm(BaseModel):
    username: str
    password: str


def create_login_router() -> APIRouter:
    """
    로그인 및 로그아웃 라우트를 포함하는 FastAPI 라우터를 생성합니다.
    
    Returns:
        FastAPI APIRouter 객체
    """
    router = APIRouter()
    
    @router.get(config.get("login_path", "/swaguard/login"), response_class=HTMLResponse, include_in_schema=False)
    async def login_page(request: Request, next: Optional[str] = None):
        """로그인 페이지를 제공합니다."""
        login_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SwagGuard Login</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f8f9fa;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .login-container {{
                    background-color: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 360px;
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 1.5rem;
                }}
                .form-group {{
                    margin-bottom: 1rem;
                }}
                label {{
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: bold;
                }}
                input {{
                    width: 100%;
                    padding: 0.5rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 1rem;
                }}
                button {{
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 0.75rem 1rem;
                    border-radius: 4px;
                    cursor: pointer;
                    width: 100%;
                    font-size: 1rem;
                    margin-top: 1rem;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
                .error-message {{
                    color: #dc3545;
                    margin-top: 1rem;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>SwagGuard Login</h1>
                <form method="post">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <input type="hidden" name="next" value="{next or '/docs'}">
                    <button type="submit">Login</button>
                    <div id="error-message" class="error-message"></div>
                </form>
            </div>
            <script>
                // URL에서 에러 메시지 파라미터 가져오기
                const urlParams = new URLSearchParams(window.location.search);
                const error = urlParams.get('error');
                if (error) {{
                    document.getElementById('error-message').textContent = decodeURIComponent(error);
                }}
            </script>
        </body>
        </html>
        """
        return login_html
    
    @router.post(config.get("login_path", "/swaguard/login"), include_in_schema=False)
    async def login(
        response: Response,
        username: str = Form(...),
        password: str = Form(...),
        next: str = Form("/docs")
    ):
        """로그인 요청을 처리합니다."""
        # 사용자 인증
        if not authenticate_user(username, password):
            # 인증 실패 시 오류 메시지와 함께 로그인 페이지로 리다이렉트
            login_path = config.get("login_path", "/swaguard/login")
            error_message = "Invalid username or password"
            redirect_url = f"{login_path}?error={error_message}"
            if next and next != "/docs":
                redirect_url += f"&next={next}"
            return RedirectResponse(redirect_url, status_code=303)
        
        # 인증 성공 시 쿠키 생성
        cookie_value, cookie_options = create_auth_cookie(username)
        
        # 쿠키 설정
        cookie_name = config.get("cookie_name", "swaguard_auth")
        response = RedirectResponse(next, status_code=303)
        response.set_cookie(
            key=cookie_name,
            value=cookie_value,
            httponly=True,
            secure=cookie_options["secure"] == "true",
            samesite=cookie_options["samesite"],
            path="/",
            max_age=int(cookie_options["max-age"])
        )
        
        return response
    
    @router.get(config.get("logout_path", "/swaguard/logout"))
    async def logout():
        """로그아웃 요청을 처리합니다."""
        # 쿠키 삭제
        cookie_name = config.get("cookie_name", "swaguard_auth")
        json_response = JSONResponse(
            content={"message": "Logged out successfully. Please refresh the page."},
            status_code=200
        )
        json_response.delete_cookie(
            key=cookie_name,
            path="/",
            secure=config.get("cookie_secure", True),
            httponly=config.get("cookie_httponly", True)
        )
        
        return json_response
    
    return router
