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
) -> List[LectureDetailsBySubCategoryResponse] | None:
    try:
        logging.info(f"{RPIN} : {request.model_dump()}")
        url = os.getenv("HYDER_AI_SC_URL")
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": "https://www.hyder.ai",
            "referer": "https://www.hyder.ai/",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 "
                          "Mobile Safari/537.36 Edg/140.0.0.0",
        }

        query_params = request.model_dump()
        r = requests.get(url=url, params=query_params, headers=headers, timeout=10)
        r.raise_for_status()  # Raises HTTPError if status != 200

        lecture_items = [
            LectureDetailsBySubCategoryResponse(**item)
            for item in r.json().get("items", [])
        ]

        logging.info(f"{RPOUT} : {lecture_items}")
        return lecture_items

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in get_lecture_details: {e}", exc_info=True)
        return None
    except ValueError as e:
        logging.error(f"JSON parsing error in get_lecture_details: {e}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error in get_lecture_details: {e}", exc_info=True)
        return None


def translate_text(
    request: TranslationServiceRequest,
) -> TranslationServiceResponse | None:
    try:
        logging.info(f"{RPIN} : {request.model_dump()}")
        url = os.getenv("HYDER_AI_TRANSLATION_URL")
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": "https://www.hyder.ai",
            "referer": "https://www.hyder.ai/",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 "
                          "Mobile Safari/537.36 Edg/140.0.0.0",
        }
        r = requests.post(
            url=url,
            json=request.model_dump(),
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()  # Raises HTTPError if status != 200

        translation_response = TranslationServiceResponse(**r.json())
        logging.info(f"{RPOUT} : {translation_response}")
        return translation_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in translate_text: {e}", exc_info=True)
        return None
    except ValueError as e:
        logging.error(f"JSON parsing error in translate_text: {e}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error in translate_text: {e}", exc_info=True)
        return None
        