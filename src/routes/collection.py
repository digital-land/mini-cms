from fastapi import APIRouter, Request, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
from src.routes.auth import get_current_user
from src.services.github_service import GithubService
from src.templates import views
import os
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any, Tuple
import uuid

DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo

router = APIRouter()

def get_collection(github_service: GithubService, collection_id: str) -> Dict:
    """Get collection configuration by ID."""
    data_config = github_service.get_repo_content_for_path(DATA_REPO, "config.yml", format="yaml")
    collection = next((c for c in data_config.get("collections", []) if c.get("id") == collection_id), None)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

def get_collection_items(github_service: GithubService, collection_id: str) -> List[Dict]:
    items = []
    try:
        items = github_service.list_files_in_directory(DATA_REPO, f"/data/collections/{collection_id}")
        # Filter out directories and non-YAML files
        items = [item for item in items if item.get("type") == "file" and
                (item.get("name").endswith(".yml") or item.get("name").endswith(".yaml"))]
        # Transform items to get their content
        items = list(map(
            lambda item: github_service.get_repo_content_for_path(
                DATA_REPO, f"/data/collections/{collection_id}/{item.get('name')}", format="yaml"
            ),
            items
        ))
    except Exception as e:
        print(f"Error listing files in directory: {str(e)}")

    return items

def get_collection_item(github_service: GithubService, collection_id: str, item_id: str) -> Dict:
    return github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml"
    )

def get_field_by_path(collection: Dict, field_path: str) -> Tuple[Dict, Any, List[str]]:
    """Get field configuration and data by path.

    Args:
        collection: Collection configuration
        field_path: Path to the field (e.g. "field1/0/field2/1")

    Returns:
        Tuple containing:
        - Field configuration
        - Field data
        - List of path parts
    """
    field_parts = field_path.split("/")
    if len(field_parts) not in [2, 4]:
        raise HTTPException(status_code=400, detail="Invalid field path format")

    # Get first level field
    field = next((f for f in collection.get("fields", []) if f.get("id") == field_parts[0]), None)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    # Get second level field if needed
    if len(field_parts) > 2:
        field = next((f for f in field.get("fields", []) if f.get("id") == field_parts[2]), None)
        if not field:
            raise HTTPException(status_code=404, detail="Nested field not found")

    return field, field_parts


def get_field_data(item_data: Dict, field_parts: List[str]) -> Any:
    """Get field data from item data using field path parts."""
    try:
        data = item_data.get("data", {})
        if len(field_parts) == 2:
            return data.get(field_parts[0], [])[int(field_parts[1])]
        else:
            return data.get(field_parts[0], [])[int(field_parts[1])].get(field_parts[2], [])[int(field_parts[3])]
    except (IndexError, KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid field data structure")


def update_field_data(item_data: Dict, field_parts: List[str], field_data: Dict) -> None:
    """Update field data in item data using field path parts."""
    try:
        if len(field_parts) == 2:
            item_data["data"][field_parts[0]][int(field_parts[1])] = field_data
        else:
            item_data["data"][field_parts[0]][int(field_parts[1])][field_parts[2]][int(field_parts[3])] = field_data
    except (IndexError, KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid field data structure")


@router.get("/{collection_id}")
async def index(request: Request, user: dict = Depends(get_current_user), collection_id: str = Path(..., description="The ID of the collection to retrieve")):
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    items = get_collection_items(github_service, collection_id)

    return views.TemplateResponse(
        request=request,
        name="collection/collection.html",
        context={"user": user, "collection": collection, "items": items}
    )


@router.get("/{collection_id}/{item_id}")
async def item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve")
):
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml"
    )

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
    item_id: str = Path(..., description="The ID of the item to retrieve")
):
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml"
    )

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
    item_id: str = Path(..., description="The ID of the item to retrieve")
):
    item_file_path = f"/data/collections/{collection_id}/{item_id}.yml"
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, item_file_path, format="yaml", get_sha=True
    )

    item_content = item.get("content")
    editable_fields = [field.get("id") for field in collection.get("fields", []) if field.get("editable") and field.get("editable") == True]
    form_data = await request.form()

    for field in editable_fields:
        item_content["data"][field] = form_data.get(field)

    github_service.update_repo_content(
        DATA_REPO,
        item_file_path,
        item_content,
        format="yaml",
        commit_message=f"Update collection item {collection_id}/{item_id}",
        sha=item.get("sha")
    )

    return RedirectResponse(url=request.url_for("item", collection_id=collection_id, item_id=item_id), status_code=303)


@router.get("/{collection_id}/{item_id}/edit/fields/{field_path:path}")
async def edit_repeatable_item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve"),
    field_path: str = Path(..., description="The path of the field to retrieve")
):
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml"
    )

    field, field_parts = get_field_by_path(collection, field_path)
    repeatable_field_data = get_field_data(item, field_parts)

    return views.TemplateResponse(
        request=request,
        name="collection/edit/edit-repeatable-collection-item.html",
        context={
            "user": user,
            "item": item,
            "collection": collection,
            "field_path": field_path,
            "repeatable_field": field,
            "repeatable_field_data": repeatable_field_data
        }
    )


@router.post("/{collection_id}/{item_id}/update/fields/{field_path:path}")
async def update_repeatable_item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve"),
    field_path: str = Path(..., description="The path of the field to retrieve")
):
    item_file_path = f"/data/collections/{collection_id}/{item_id}.yml"
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, item_file_path, format="yaml", get_sha=True
    )

    item_content = item.get("content")
    form_data = await request.form()
    field, field_parts = get_field_by_path(collection, field_path)

    # Get editable fields
    editable_fields = [f.get("id") for f in field.get("fields", []) if f.get("editable") and f.get("editable") == True]

    # Get current field data
    repeatable_field_data = get_field_data(item_content, field_parts)

    # Update field data
    for field_id in editable_fields:
        repeatable_field_data[field_id] = form_data.get(field_id)

    # Update the item content
    update_field_data(item_content, field_parts, repeatable_field_data)

    # Update the item in the repository
    github_service.update_repo_content(
        DATA_REPO,
        item_file_path,
        item_content,
        format="yaml",
        commit_message=f"Update collection item {collection_id}/{item_id}",
        sha=item.get("sha")
    )

    return RedirectResponse(url=request.url_for("edit_repeatable_item", collection_id=collection_id, item_id=item_id, field_path=field_path), status_code=303)


@router.get("/{collection_id}/{item_id}/new/fields/{field_id:path}")
async def new_repeatable_item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve"),
    field_id: str = Path(..., description="The ID of the field to retrieve")
):
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, f"/data/collections/{collection_id}/{item_id}.yml", format="yaml"
    )

    repeatable_field = next((f for f in collection.get("fields", []) if f.get("id") == field_id), None)

    return views.TemplateResponse(
        request=request,
        name="collection/new/new-repeatable-collection-item.html",
        context={
            "user": user,
            "item": item,
            "collection": collection,
            "repeatable_field": repeatable_field,
            "field_id": field_id
        }
    )

@router.post("/{collection_id}/{item_id}/new/fields/{field_id}")
async def create_repeatable_item(
    request: Request,
    user: dict = Depends(get_current_user),
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve"),
    field_id: str = Path(..., description="The ID of the field to retrieve")
):
    item_file_path = f"/data/collections/{collection_id}/{item_id}.yml"
    github_service = GithubService(access_token=user.get("access_token"))
    collection = get_collection(github_service, collection_id)
    item = github_service.get_repo_content_for_path(
        DATA_REPO, item_file_path, format="yaml", get_sha=True
    )

    item_content = item.get("content")
    form_data = await request.form()

    # Get the repeatable field
    repeatable_field = next((f for f in collection.get("fields", []) if f.get("id") == field_id), None)

    # Create a new item
    new_item = {}

    for field in repeatable_field.get("fields", []):
        if (form_data.get(field.get("id")) is None or form_data.get(field.get("id")) == '') and field.get("default_value") == 'generate_uuid()':
            new_item[field.get("id")] = str(uuid.uuid4())
        else:
            new_item[field.get("id")] = form_data.get(field.get("id"))

    # Update the item content
    item_content["data"][field_id].append(new_item)

    # Update the item in the repository
    github_service.update_repo_content(
        DATA_REPO,
        item_file_path,
        item_content,
        format="yaml",
        commit_message=f"Create new collection item {collection_id}/{item_id}",
        sha=item.get("sha")
    )

    return RedirectResponse(url=request.url_for("item", collection_id=collection_id, item_id=item_id), status_code=303)
