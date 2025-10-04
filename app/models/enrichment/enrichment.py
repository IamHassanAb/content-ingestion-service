from typing import List
from pydantic import BaseModel, Field


class MetaDataEnrichmentRequest(BaseModel):
    title: str = Field(description="The title of the content")
    content: str = Field(description="The content to extract enriched metadata.")


class MetaDataEnrichmentResponse(BaseModel):
    tags: List[str] = Field(description="The list of tags extracted from the content.")
    summary: str = Field(description="A brief summary generated from the content.")
