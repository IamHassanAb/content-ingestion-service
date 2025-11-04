from fastapi import FastAPI
from ..api.v1.endpoints.ingestion import router as ingestion_router

# from ..api.v1.endpoints.health import router as health_router
from ..api.v1.endpoints.pipeline import router as pipeline_router
from ..api.v1.endpoints.items import router as item_router
from ..api.v1.endpoints.enrichment import router as enrichment_router


def register_routes(app: FastAPI):
    app.include_router(ingestion_router)
    app.include_router(enrichment_router)
    app.include_router(item_router)
    app.include_router(pipeline_router)