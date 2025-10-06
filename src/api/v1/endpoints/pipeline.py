# I might need this in the future.
from fastapi import APIRouter, HTTPException
from src.models.pipeline.Pipeline import (
    PipelineRequest,
    PipelineResponse,
)
from src.services.pipeline import run_pipeline

# from app.database import get_db


router = APIRouter(
    prefix="/pipeline",
    tags=["pipeline"],
    responses={404: {"description": "Not found"}},
)


@router.post("/execute", response_model=PipelineResponse)
async def enrich(pipelineRequest: PipelineRequest):
    try:
        pipelineResponse = run_pipeline(pipelineRequest)
        return pipelineResponse
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
