from fastapi import APIRouter, Request, Path
from fastapi.responses import JSONResponse
from src.services.github_service import GithubService
from src.routes.collection import get_collection, get_collection_items, get_collection_item
import os
import json
from datetime import datetime
from typing import Any

DATA_REPO = os.environ.get("DATA_REPO", "")  # Format: owner/repo

router = APIRouter()

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects and other non-serializable types."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_for_json(data: Any) -> Any:
    """Recursively serialize data to be JSON compatible."""
    if isinstance(data, dict):
        return {key: serialize_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

@router.get("/v1/collections/{collection_id}")
async def collection(
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
):
    github_service = GithubService()
    collection = get_collection(github_service, collection_id)
    items = get_collection_items(github_service, collection_id)

    return JSONResponse(content=serialize_for_json({
        "collection": {
            **collection,
            "items": items
        }
    }))


@router.get("/v1/collections/{collection_id}/{item_id}")
async def collection_item(
    collection_id: str = Path(..., description="The ID of the collection to retrieve"),
    item_id: str = Path(..., description="The ID of the item to retrieve")
):
    github_service = GithubService()
    collection = get_collection(github_service, collection_id)
    item = get_collection_item(github_service, collection_id, item_id)

    return JSONResponse(content=serialize_for_json({
        "data": item.get("data", {}),
        "metadata": {
            "collection": collection,
        }
    }))
