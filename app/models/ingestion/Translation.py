from pydantic import BaseModel
from typing import Optional


class TranslationServiceRequest(BaseModel):
    item_id: str
    target_lang_code: str
    target_lang_name: str


class TranslationServiceResponse(BaseModel):
    title: str
    translation: str
