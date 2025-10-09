from src.services.redis_service import set_lecture_dto
from src.models.enrichment.enrichment import (
    MetaDataEnrichmentRequest,
    MetaDataEnrichmentResponse,
)
from src.models.enrichment.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)
from src.models.item import (
    ItemSchema,
    Content,
    DateInfo,
    Author,
    Organisation,
    Media,
    Audience,
    Provenance,
)
from src.models.ingestion.LectureDetailsByScholar import (
    LectureDetailsByScholarResponse,
)
from src.services.enrichment_service import translate_text, get_enrichment_components
from src.models.pipeline.Pipeline import PipelineRequest, PipelineResponse
import logging
from src.utils.constants import RPIN, RPOUT


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

    # Step 3: Combine relevant data to fill all the details
    pipelineResponse = hydrate_pipeline_response(
        pipelineRequest, metaDataEnrichmentResponse, translateServiceResponse
    )

    #Step 4: Store the pipelineResponse in redis cache.
    set_lecture_dto(pipelineResponse.to_flat_dict())
    
    logging.info(f"{RPOUT} : {pipelineResponse.model_dump()}")
    # Step 3: Return response
    return pipelineResponse


def hydrate_pipeline_response(
    pipelineRequest: PipelineRequest,
    metaDataEnrichmentResponse: MetaDataEnrichmentResponse,
    translateServiceResponse: TranslationServiceResponse,
) -> PipelineResponse:
    """Fill the PipelineResponse with complete item data."""
    lecture_details: LectureDetailsByScholarResponse = (
        pipelineRequest.lecture_details_by_scholar
    )
    if lecture_details is None:
        return {"error": "Lecture details are missing in the pipeline request."}

    item = ItemSchema(
        id=pipelineRequest.item_id,
        title=translateServiceResponse.title,
        type="lecture",
        language=lecture_details.language,
        author=Author(
            id=lecture_details.scholar.id,
            name=lecture_details.scholar.name,
            city=lecture_details.scholar.city,
            country=lecture_details.scholar.country,
            language=lecture_details.scholar.language,
        ),
        organisation=Organisation(
            id=lecture_details.centre.id,
            name=lecture_details.centre.name,
            city=lecture_details.centre.city,
            country=lecture_details.centre.country,
        ),
        content=Content(
            tags=metaDataEnrichmentResponse.tags,
            summary=metaDataEnrichmentResponse.summary,
            translation=translateServiceResponse.translation,
        ),
        date=DateInfo(
            gregorian=lecture_details.itemDate, islamic=lecture_details.islamicDate
        ),
        quranReference=None,
        hadithReference=None,
        media=Media(
            audioFile=lecture_details.audioFile,
            videoFile=None,
            imageFile=lecture_details.imageFile,
            pdfFile=None,
            link=lecture_details.link,
        ),
        audience=Audience(level="all", intendedAudience=[]),
        provenance=Provenance(
            createdBy=(
                lecture_details.createdBy.fullName
                if lecture_details.createdBy
                else None
            ),
            updatedBy=(
                lecture_details.updatedBy.fullName
                if lecture_details.updatedBy
                else None
            ),
            createdAt=lecture_details.createdAt,
            updatedAt=lecture_details.updatedAt,
        ),
    )
    pipelineResponse = PipelineResponse(item=item)
    return pipelineResponse
