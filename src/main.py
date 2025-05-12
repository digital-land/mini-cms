import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.services.github_service import GithubService
from src.routes.auth import router as auth_router, get_current_user
from src.routes.collection import router as collection_router
# Load environment variables from .env file
load_dotenv()

APP_HOST = os.environ["APP_HOST"]
DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo
# You should set this in .env
SECRET_KEY = os.environ.get("APP_KEY", "your-secret-key")

app = FastAPI(servers=[{"url": APP_HOST}])
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static/dist"), name="static")
app.mount("/assets", StaticFiles(directory="src/static/assets"),
          name="static_assets")

views = Jinja2Templates(directory="src/views")

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(collection_router, prefix="/collections", tags=["collections"], dependencies=[Depends(get_current_user)])


@app.get("/")
async def read_root(request: Request, user: dict = Depends(get_current_user)):
    github_service = GithubService(access_token=user.get("access_token"))
    data_config = github_service.get_repo_content_for_path(
        DATA_REPO, "config.yml", format="yaml")
    collections = data_config.get("collections", [])

    return views.TemplateResponse(
        request=request, name="index.html", context={"user": user, "collections": collections}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    raise exc
