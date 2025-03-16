import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.github import GithubSSO
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
load_dotenv()

HOST = os.environ["APP_HOST"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
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
    allow_insecure_http=True,
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
    request.session["user"] = dict(user)
    return RedirectResponse(url="/")

@app.get("/auth/logout")
async def auth_logout(request: Request):
    """Logout"""
    request.session.clear()
    return RedirectResponse(url="/auth/login")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    raise exc
