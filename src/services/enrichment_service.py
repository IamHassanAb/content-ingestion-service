from src.models.enrichment.enrichment import (
    MetaDataEnrichmentRequest,
    MetaDataEnrichmentResponse,
)
from ..models.enrichment.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)
import requests
from src.utils.constants import RPIN, RPOUT
import logging
import os
from src.llm.enrich import get_enricher_response


def get_enrichment_components(
    metadataEnrichmentRequest: MetaDataEnrichmentRequest,
) -> MetaDataEnrichmentResponse:
    """Enrich metadata using LLM."""
    logging.info(f"{RPIN} : {metadataEnrichmentRequest.model_dump()}")
    metadataEnrichmentResponse = MetaDataEnrichmentResponse.model_validate_json(
        get_enricher_response(metadataEnrichmentRequest)
    )
    logging.info(f"{RPOUT} : {metadataEnrichmentResponse.model_dump()}")
    return metadataEnrichmentResponse


def translate_text(
    translationServiceRequest: TranslationServiceRequest,
) -> TranslationServiceResponse | None:
    try:
        logging.info(f"{RPIN} : {translationServiceRequest.model_dump()}")
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
            json=translationServiceRequest.model_dump(),
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()  # Raises HTTPError if status != 200

        translation_response = TranslationServiceResponse.model_validate(r.json())
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
