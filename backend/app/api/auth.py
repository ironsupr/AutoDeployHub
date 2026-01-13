from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
import httpx
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.get("/login")
async def login():
    if not settings.GITHUB_CLIENT_ID:
        return {"error": "GitHub OAuth not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET."}
    
    github_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope=user"
    return RedirectResponse(url=github_url)

@router.get("/callback")
async def callback(code: str, response: Response):
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for access token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            params={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        token_resp_json = token_resp.json()
        access_token = token_resp_json.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")

        # 2. Get user info
        user_resp = await client.get(
            "https://github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = user_resp.json()
        username = user_data.get("login")

        # 3. Create our own JWT and set in cookie
        jwt_token = create_access_token({"sub": username})
        
        redirect = RedirectResponse(url="/dashboard")
        redirect.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
        return redirect

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/dashboard")
    response.delete_cookie("access_token")
    return response

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None
    
    token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            return None
        return username
    except JWTError:
        return None
