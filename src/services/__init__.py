import redis
import os
from typing import Optional
from src.models.pipeline.Pipeline import PipelineResponse

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # 1 hour default

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def set_pipeline_dto(
    item_id: str, dto: PipelineResponse, ttl: Optional[int] = REDIS_TTL
):
    r.set(f"pipeline:{item_id}", dto.model_dump_json(), ex=ttl)


def get_pipeline_dto(item_id: str) -> PipelineResponse | None:
    raw = r.get(f"pipeline:{item_id}")
    if raw:
        return PipelineResponse.model_validate_json(raw)
    return None


def delete_pipeline_dto(item_id: str):
    r.delete(f"pipeline:{item_id}")
