from app.models.enrichment.enrichment import MetaDataEnrichmentRequest, MetaDataEnrichmentResponse
from app.llm.enrich import get_enricher_response


def enrich_metadata(input: MetaDataEnrichmentRequest) -> MetaDataEnrichmentResponse:
    """Enrich metadata using LLM."""
    response_text = get_enricher_response(input)
    return MetaDataEnrichmentResponse.model_validate_json(response_text)


