from fastapi import APIRouter, HTTPException
from typing import List
from src.models.item import ItemSchema
from src.repository.item_repo import get_item_by_id, get_all_items
from src.services.redis_service import get_lecture_dto, get_all_lectures

# from app.database import get_db


router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get-items", response_model=List[ItemSchema])
async def fetch_lecture_items():
    try:
        cache_response = get_all_lectures()
        if cache_response:
            return cache_response
        response = get_all_items()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-item-by-id/{item_id}", response_model=ItemSchema)
async def fetch_lecture_items_by_id(item_id: str):
    try:
        cache_response = get_lecture_dto(item_id=item_id)
        if cache_response:
            return cache_response
        response = get_item_by_id(item_id=item_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
