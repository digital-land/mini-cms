from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import markdown

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

def get_session_data(request: Request) -> dict:
    """Get the session data from the request.

    Args:
        request: The FastAPI request object

    Returns:
        The session data
    """
    return request.get("session", {})

views.env.globals["get_session_data"] = get_session_data

def markdown_to_html(text: str) -> str:
    """Convert Markdown to HTML.

    Args:
        text: The Markdown text to convert

    Returns:
        The HTML string
    """
    return markdown.markdown(text)

views.env.filters["markdown_to_html"] = markdown_to_html
