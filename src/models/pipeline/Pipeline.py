from pydantic import BaseModel
from typing import Optional
from src.models.ingestion.LectureDetailsByScholar import LectureDetailsByScholarResponse
from src.models.item import ItemSchema


class PipelineRequest(BaseModel):
    item_id: str
    target_lang_code: str
    target_lang_name: str
    lecture_details_by_scholar: Optional[LectureDetailsByScholarResponse]

    # def model_dump(self, **kwargs):
    #     # Call the default model_dump
    #     data = super().model_dump(**kwargs)
    #     # Pop the extra model and merge its fields
    #     lecture_details_by_scholar = data.pop("lecture_details_by_scholar", {})
    #     return {**lecture_details_by_scholar, **data}


class PipelineResponse(BaseModel):
    item: ItemSchema

    def to_flat_dict(self, **kwargs) -> dict:
        """Return a flat dict merging item fields at the top level."""
        data = super().model_dump(**kwargs)
        item = data.pop("item", None)
        if item and isinstance(item, dict):
            return {**item, **data}
        return data
