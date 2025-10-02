from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.ingestion.LectureDetailsByScholar import LectureDetailsByScholarRequest, LectureDetailsByScholarResponse
from app.models.ingestion.Translation import TranslationServiceRequest, TranslationServiceResponse
from app.services.ingestion_service import get_lecture_details, translate_text
# from app.database import get_db


router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    responses={404: {"description": "Not found"}},
)

@router.get("/lecture-details", response_model=List[LectureDetailsByScholarResponse])
async def fetch_lecture_details(request: LectureDetailsByScholarRequest = Depends()):
    try:
        response = get_lecture_details(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=TranslationServiceResponse)
async def translate(request: TranslationServiceRequest):
    try:
        response = translate_text(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

