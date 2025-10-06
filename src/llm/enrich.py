import os
from groq import Groq
from src.llm.prompts import get_prompt
from src.models.enrichment.enrichment import MetaDataEnrichmentRequest


def get_enricher_response(input: MetaDataEnrichmentRequest) -> str:
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": get_prompt(input),
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content
