import requests
from typing import List
from ..utils.constants import *
import logging
import os
from ..models.ingestion.LectureDetailsBySubCategory import (
    LectureDetailsBySubCategoryRequest,
    LectureDetailsBySubCategoryResponse,
)
from ..models.ingestion.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)


def get_lecture_details(
    request: LectureDetailsBySubCategoryRequest,
) -> List[LectureDetailsBySubCategoryResponse]:
    try:
        logging.info(f"{RPIN} : {request.model_dump()}")
        url = os.getenv("HYDER_AI_SC_URL")
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": "https://www.hyder.ai",
            "referer": "https://www.hyder.ai/",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36 Edg/140.0.0.0",
        }

        query_params = request.model_dump()
        r = requests.get(url=url, params=query_params, headers=headers)
        lecture_items = [LectureDetailsBySubCategoryResponse(**item) for item in r.json()["items"]]
        logging.info(f"{RPOUT} : {lecture_items}")
        return lecture_items
    except:
        pass
