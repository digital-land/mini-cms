from fastapi import APIRouter, Request, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
from src.routes.auth import get_current_user
from src.services.github_service import GithubService
import os
from fastapi.templating import Jinja2Templates

DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo

router = APIRouter()
views = Jinja2Templates(directory="src/views")

@router.get("/{collection_id}")
async def index(request: Request, user: dict = Depends(get_current_user), collection_id: str = Path(..., description="The ID of the collection to retrieve")):
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
        request=request, name="collection/collection.html", context={"user": user, "collection": collection, "items": items}
    )

@router.get("/{collection_id}/{item_id}")
async def item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve")):

    github_service = GithubService(access_token=user.get("access_token"))
    collection = next((c for c in github_service.get_repo_content_for_path(
        DATA_REPO, f"/config.yml", format="yaml").get("collections", []) if c.get("id") == collection_id), None)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml")

    return views.TemplateResponse(
        request=request,
        name="collection/collection-item.html",
        context={"user": user, "item": item, "collection": collection}
    )

@router.get("/{collection_id}/{item_id}/edit")
async def edit_item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve")):

    github_service = GithubService(access_token=user.get("access_token"))
    collection = next((c for c in github_service.get_repo_content_for_path(
        DATA_REPO, f"/config.yml", format="yaml").get("collections", []) if c.get("id") == collection_id), None)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml")

    return views.TemplateResponse(
        request=request,
        name="collection/edit/edit-collection-item.html",
        context={"user": user, "item": item, "collection": collection}
    )

@router.post("/{collection_id}/{item_id}/update")
async def update_item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve")):
    item_file_path = f"/data/collections/{collection_id}/{item_id}.yml"

    ## Get the collection
    github_service = GithubService(access_token=user.get("access_token"))
    collection = next((c for c in github_service.get_repo_content_for_path(
        DATA_REPO, f"/config.yml", format="yaml").get("collections", []) if c.get("id") == collection_id), None)

    ## Get the collection item
    item = github_service.get_repo_content_for_path(
        DATA_REPO, item_file_path, format="yaml", get_sha=True)

    item_content = item.get("content")

    ## Get the editable fields
    editable_fields = [field.get("id") for field in collection.get("fields", []) if field.get("editable")]

    ## Get the form data
    form_data = await request.form()

    ## Update the item
    for field in editable_fields:
        item_content["data"][field] = form_data.get(field)

    ## Update the item in the repository
    github_service.update_repo_content(
        DATA_REPO, item_file_path, item_content, format="yaml", commit_message=f"Update collection item {collection_id}/{item_id}", sha=item.get("sha"))

    return RedirectResponse(url=f"/collections/{collection_id}/{item_id}", status_code=303)
