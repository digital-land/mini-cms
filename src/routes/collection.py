from fastapi import APIRouter, Request, Depends
from src.routes.auth import get_current_user
from src.services.github_service import GithubService
import os
from fastapi.templating import Jinja2Templates
from fastapi import Path, HTTPException

DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo

router = APIRouter()
views = Jinja2Templates(directory="src/views")

@router.get("/{collection_id}")
async def get_collection(request: Request, user: dict = Depends(get_current_user), collection_id: str = Path(..., description="The ID of the collection to retrieve")):
    github_service = GithubService(access_token=user.get("access_token"))
    data_config = github_service.get_repo_content_for_path(
        DATA_REPO, "config.yml", format="yaml")
    config = data_config.get("collections", [])
    collection = next((c for c in config if c.get("id") == collection_id), None)

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    items = []

    try:
        items = github_service.list_files_in_directory(
            DATA_REPO, f"/data/collections/{collection_id}"
        )
    except Exception as e:
        print("Error listing files in directory")
        print(e)

    # Filter out directories
    items = [item for item in items if item.get("type") == "file" and (item.get("name").endswith(".yml") or item.get("name").endswith(".yaml"))]

    # Transform items to get their content
    items = list(map(
        lambda item: github_service.get_repo_content_for_path(
            DATA_REPO, f"/data/collections/{collection_id}/{item.get('name')}", format="yaml"
        ),
        items
    ))

    return views.TemplateResponse(
        request=request, name="collection.html", context={"user": user, "collection": collection, "items": items}
    )

