from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.models.ingestion.LectureDetailsByScholar import (
    LectureDetailsByScholarRequest,
    LectureDetailsByScholarResponse,
)
from src.services.ingestion_service import get_lecture_details

# from app.database import get_db


router = APIRouter(
    prefix="/ingest",
    tags=["ingest"],
    responses={404: {"description": "Not found"}},
)


@router.get("/lecture-details", response_model=List[LectureDetailsByScholarResponse])
async def fetch_lecture_details(request: LectureDetailsByScholarRequest = Depends()):
    try:
        response = get_lecture_details(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
