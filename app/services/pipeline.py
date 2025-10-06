from app.models.enrichment.enrichment import (
    MetaDataEnrichmentRequest,
    MetaDataEnrichmentResponse,
)
from app.models.enrichment.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)
from app.services.enrichment_service import translate_text, get_enrichment_components
from app.models.pipeline.Pipeline import PipelineRequest, PipelineResponse
import logging
from app.utils.constants import RPIN, RPOUT


def run_pipeline(pipelineRequest: PipelineRequest) -> PipelineResponse:
    """Run the full pipeline: translation and metadata enrichment."""
    logging.info(f"{RPIN}: {pipelineRequest.model_dump()}")
    # Step 1: Translate the input text
    translationServiceRequest = TranslationServiceRequest(
        item_id=pipelineRequest.item_id,
        target_lang_code=pipelineRequest.target_lang_code,
        target_lang_name=pipelineRequest.target_lang_name,
    )
    translateServiceResponse = TranslationServiceResponse.model_validate(
        translate_text(translationServiceRequest)
    )

    # Step 2: Enrich metadata based on the translated text
    metaDataEnrichmentRequest = MetaDataEnrichmentRequest(
        title=translateServiceResponse.title,
        content=translateServiceResponse.translation,
    )
    metaDataEnrichmentResponse = MetaDataEnrichmentResponse.model_validate(
        get_enrichment_components(metaDataEnrichmentRequest)
    )

    #TODO: Add a step to fill the whole Item (to be stored in the db)
    pipelineResponse = PipelineResponse(
        item_id=translationServiceRequest.item_id,
        title=translateServiceResponse.title,
        content=translateServiceResponse.translation,
        tags=metaDataEnrichmentResponse.tags,
        summary=metaDataEnrichmentResponse.summary,
    )
    logging.info(f"{RPOUT} : {pipelineResponse.model_dump()}")
    # Step 3: Combine results into a single response
    return pipelineResponse
