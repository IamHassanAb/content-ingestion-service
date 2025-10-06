from pydantic import BaseModel, Field
from typing import List
from app.models.ingestion.LectureDetailsByScholar import LectureDetailsByScholarResponse


class PipelineRequest(BaseModel):
    item_id: str
    target_lang_code: str
    target_lang_name: str
    lecture_details_by_scholar: LectureDetailsByScholarResponse

    # def model_dump(self, **kwargs):
    #     # Call the default model_dump
    #     data = super().model_dump(**kwargs)
    #     # Pop the extra model and merge its fields
    #     lecture_details_by_scholar = data.pop("lecture_details_by_scholar", {})
    #     return {**lecture_details_by_scholar, **data}


class PipelineResponse(BaseModel):
    item_id: str
    title: str = Field(description="The title of the content")
    content: str = Field(description="The content to extract enriched metadata.")
    tags: List[str] = Field(description="The list of tags extracted from the content.")
    summary: str = Field(description="A brief summary generated from the content.")
