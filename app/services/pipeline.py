from app.models.enrichment.enrichment import MetaDataEnrichmentRequest, MetaDataEnrichmentResponse
from app.models.ingestion.Translation import TranslationServiceRequest, TranslationServiceResponse
from app.services.ingestion_service import translate_text
from app.services.enrichment_service import enrich_metadata

def run_pipeline(input: TranslationServiceRequest) -> MetaDataEnrichmentResponse:
    """Run the full pipeline: translation and metadata enrichment."""
    # Step 1: Translate the input text
    translate_service_response = translate_text(input)
    
    # Step 2: Enrich metadata based on the translated text
    enrichment_request = MetaDataEnrichmentRequest(
        title=translate_service_response.title,
        content=translate_service_response.translation
    )
    enriched_metadata = enrich_metadata(enrichment_request)
    
    # Step 3: Combine results into a single response
    return MetaDataEnrichmentResponse(
        title=translate_service_response.title,
        content=translate_service_response.translation,
        tags=enriched_metadata.tags,
        summary=enriched_metadata.summary,
    )