from pydantic import BaseModel, Field
from typing import List


class PipelineRequest(BaseModel):
    item_id: str
    target_lang_code: str
    target_lang_name: str


class PipelineResponse(BaseModel):
    item_id: str
    title: str = Field(description="The title of the content")
    content: str = Field(description="The content to extract enriched metadata.")
    tags: List[str] = Field(description="The list of tags extracted from the content.")
    summary: str = Field(description="A brief summary generated from the content.")
