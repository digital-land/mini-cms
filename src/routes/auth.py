import os
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.github import GithubSSO
from src.services.github_service import GithubService

# Load environment variables
HOST = os.environ["APP_HOST"]
CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]
DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo

router = APIRouter()

sso = GithubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=f"{HOST}/auth/callback",
    allow_insecure_http=HOST.startswith("http://localhost"),
)


async def get_current_user(request: Request):
    session_user = request.session.get("user")

    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    github_service = GithubService(
        access_token=session_user.get("access_token"))
    user = github_service.get_current_user()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return {**user, "access_token": session_user.get("access_token")}


@router.get("/user")
async def auth_user(user: dict = Depends(get_current_user)):
    """Get current user"""
    return user


@router.get("/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await sso.get_login_redirect()


@router.get("/callback")
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


@router.get("/logout")
async def auth_logout(request: Request):
    """Logout"""
    request.session.clear()
    return RedirectResponse(url="/auth/login")


@router.get("/check-repo-access")
async def check_repo_access(request: Request, user: dict = Depends(get_current_user)):
    """Check if the current user has read and write access to the DATA_REPO"""
    if not DATA_REPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DATA_REPO environment variable is not set"
        )

    access_token = request.session.get("user").get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token found"
        )

    github_service = GithubService(access_token=access_token)

    return github_service.check_repo_access(DATA_REPO)