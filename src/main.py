import os
from fastapi import FastAPI, Request
from fastapi_sso.sso.github import GithubSSO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

HOST = os.environ["HOST"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = GithubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=f"{HOST}/auth/callback",
    allow_insecure_http=True,
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    user = await sso.verify_and_process(request)
    return user
