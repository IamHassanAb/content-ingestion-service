import redis
import os
from typing import Optional
from src.models.item import ItemSchema

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 1))
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # 1 hour default

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def set_lecture_dto(dto: dict, ttl: Optional[int] = REDIS_TTL):
    itemDto = ItemSchema.model_validate(dto)
    r.set(f"lecture:{itemDto.id}", dto, ex=ttl)


def get_lecture_dto(item_id: str) -> ItemSchema | None:
    raw = r.get(f"lecture:{item_id}")
    if raw:
        return ItemSchema.model_validate_json(raw)
    return None


def get_all_lectures() -> list[ItemSchema]:
    keys = r.keys("lecture:*")
    lectures = []
    for key in keys:
        raw = r.get(key)
        if raw:
            lectures.append(ItemSchema.model_validate_json(raw))
    return lectures


def delete_pipeline_dto(item_id: str):
    r.delete(f"lecture:{item_id}")
