from app.models.enrichment.enrichment import (
    MetaDataEnrichmentRequest,
    MetaDataEnrichmentResponse,
)


def get_prompt(input: MetaDataEnrichmentRequest) -> str:
    """Generate the prompt for metadata enrichment."""
    return f"""You are a metadata enrichment assistant.

Input (JSON): {MetaDataEnrichmentRequest(**input).model_dump_json()}
Output (JSON) must follow this schema:
{MetaDataEnrichmentResponse.model_json_schema(mode='serialization')}

Rules:
1. Output must be **valid JSON only** (no explanatory text, no Markdown).
2. tags:
   - Return between **3 and 10** tags, ordered by relevance (most relevant first).
   - Use **lowercase** words or short noun-phrases (1–3 words). Join multi-word tags with hyphens (e.g., "sentiment-analysis").
   - No punctuation, no duplicates, no stopwords-only tags (e.g., avoid "the", "and").
   - Include specific entities, techniques, or keywords from the content (e.g., model names, datasets, methods).
3. summary:
   - 1–2 sentences (≈20–50 words). Capture the main objective, method, and key result or recommendation (if present).
   - Keep tone neutral and factual. Match the language of the input.
4. If information is missing, summarize what *is* present and do not hallucinate facts (do not invent numbers, datasets, or results).
5. Do not include any fields other than `tags` and `summary`.

Now transform the provided input JSON into the required output JSON.
"""
