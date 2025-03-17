import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.github import GithubSSO
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx

# Load environment variables from .env file
load_dotenv()

HOST = os.environ["APP_HOST"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo
SECRET_KEY = os.environ.get("APP_KEY", "your-secret-key")  # You should set this in .env

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static/dist"), name="static")
app.mount("/assets", StaticFiles(directory="src/static/assets"), name="static_assets")

views = Jinja2Templates(directory="src/views")

sso = GithubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=f"{HOST}/auth/callback",
    allow_insecure_http=HOST.startswith("http://localhost"),
)

async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

@app.get("/")
async def read_root(request: Request, user: dict = Depends(get_current_user)):
    return views.TemplateResponse(
        request=request, name="index.html", context={"user": user}
    )

@app.get("/auth/user")
async def auth_user(user: dict = Depends(get_current_user)):
    """Get current user"""
    return user

@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await sso.get_login_redirect()

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    user = await sso.verify_and_process(request)

    # Store both user info and access token in session
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_name": user.display_name,
        "access_token": sso.access_token,  # Store the access token
    }

    return RedirectResponse(url="/")

@app.get("/auth/logout")
async def auth_logout(request: Request):
    """Logout"""
    request.session.clear()
    return RedirectResponse(url="/auth/login")

@app.get("/auth/check-repo-access")
async def check_repo_access(user: dict = Depends(get_current_user)):
    """Check if the current user has read and write access to the DATA_REPO"""
    if not DATA_REPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DATA_REPO environment variable is not set"
        )

    access_token = user.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token found"
        )

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = await client.get(
            f"https://api.github.com/repos/{DATA_REPO}",
            headers=headers
        )

        if response.status_code == 404:
            return {
                "has_access": False,
                "detail": "Repository not found or no access"
            }
        elif response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to check repository access"
            )

        repo_data = response.json()
        permissions = repo_data.get("permissions", {})

        return {
            "has_access": True,
            "permissions": {
                "admin": permissions.get("admin", False),
                "push": permissions.get("push", False),
                "pull": permissions.get("pull", False)
            }
        }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    raise exc
