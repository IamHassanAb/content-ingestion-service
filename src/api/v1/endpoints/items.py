from fastapi import APIRouter, HTTPException
from typing import List
from src.models.item import ( 
    ItemSchema
)
from src.repository.item_repo import get_item_by_id, get_all_items

# from app.database import get_db


router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get-items", response_model=List[ItemSchema])
async def fetch_lecture_items():
    try:
        response = get_all_items()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/get-item-by-id/{item_id}", response_model=ItemSchema)
async def fetch_lecture_items_by_id(item_id: str):
    try:
        response = get_item_by_id(item_id=item_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
