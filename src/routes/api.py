from fastapi import APIRouter, Request, Path
from fastapi.responses import JSONResponse
from src.services.github_service import GithubService
from src.routes.collection import get_collection, get_collection_items, get_collection_item
import os

DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo

router = APIRouter()

@router.get("/v1/collections/{collection_id}")
async def collection(
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
):
    github_service = GithubService()
    collection = get_collection(github_service, collection_id)
    items = get_collection_items(github_service, collection_id)

    return JSONResponse(content={
        "collection": {
            **collection,
            "items": items
        }
    })


@router.get("/v1/collections/{collection_id}/{item_id}")
async def collection_item(
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve")
):
    github_service = GithubService()
    collection = get_collection(github_service, collection_id)
    item = get_collection_item(github_service, collection_id, item_id)

    return JSONResponse(content={
        "data": item.get("data", {}),
        "metadata": {
            "collection": collection,
        }
    })
