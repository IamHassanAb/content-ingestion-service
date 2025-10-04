from fastapi import APIRouter, HTTPException
from app.models.enrichment.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)
from app.models.enrichment.enrichment import (
    MetaDataEnrichmentRequest,
    MetaDataEnrichmentResponse,
)
from app.services.enrichment_service import translate_text, enrich_metadata

# from app.database import get_db


router = APIRouter(
    prefix="/enrich",
    tags=["enrich"],
    responses={404: {"description": "Not found"}},
)


@router.post("/enrich-metadata", response_model=MetaDataEnrichmentResponse)
async def enrich(request: MetaDataEnrichmentRequest):
    try:
        response = enrich_metadata(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-translation", response_model=TranslationServiceResponse)
async def translate(request: TranslationServiceRequest):
    try:
        response = translate_text(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
