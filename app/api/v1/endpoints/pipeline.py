# I might need this in the future.
from fastapi import APIRouter, HTTPException
from app.models.enrichment.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)
from app.models.pipeline.Pipeline import (
    PipelineRequest,
    PipelineResponse,
)
from app.services.enrichment_service import translate_text, enrich_metadata

# from app.database import get_db


router = APIRouter(
    prefix="/pipeline",
    tags=["pipeline"],
    responses={404: {"description": "Not found"}},
)


@router.post("/execute", response_model=PipelineResponse)
async def enrich(pipelineRequest: PipelineRequest):
    try:
        pipelineResponse = enrich_metadata(pipelineRequest)
        return pipelineResponse
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
