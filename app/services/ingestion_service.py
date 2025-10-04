import requests
from typing import List
from app.utils.constants import RPIN, RPOUT
import logging
import os
from ..models.ingestion.LectureDetailsByScholar import (
    LectureDetailsByScholarRequest,
    LectureDetailsByScholarResponse,
)


def get_lecture_details(
    request: LectureDetailsByScholarRequest,
) -> List[LectureDetailsByScholarResponse] | None:
    try:
        logging.info(f"{RPIN} : {request.model_dump()}")
        url = os.getenv("HYDER_AI_LECTURE_DETAILS_BY_SCHOLAR_URL")
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
            LectureDetailsByScholarResponse(**item)
            for item in r.json()[0].get("items", [])
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
