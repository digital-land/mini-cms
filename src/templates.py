from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os

load_dotenv()
APP_HOST = os.environ["APP_HOST"]
views = Jinja2Templates(directory="src/views")

def secure_url_for(request: Request, name: str, **path_params: str) -> str:
    """Generate a secure URL for a given route name.

    Args:
        request: The FastAPI request object
        name: The route name
        **path_params: Path parameters for the route

    Returns:
        A secure URL string (https://)
    """
    url = request.url_for(name, **path_params)

    # Check if APP_HOST is https
    if APP_HOST.startswith("https://"):
        return str(url).replace("http://", "https://")

    return str(url)

views.env.globals["secure_url_for"] = secure_url_for

