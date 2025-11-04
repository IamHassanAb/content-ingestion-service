import logging
from celery import shared_task, group, chord
from typing import List
from celery.exceptions import MaxRetriesExceededError
from src.models.pipeline.Pipeline import PipelineRequest, PipelineResponse
from src.models.ingestion.LectureDetailsByScholar import (
    LectureDetailsByScholarRequest,
    LectureDetailsByScholarResponse,
)
from src.services.pipeline import run_pipeline
from src.services.ingestion_service import get_lecture_details
from src.repository.item_repo import insert_many_items, get_all_lecture_ids

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 3. THE PRODUCER (Scheduled Task using Chord)
# ---------------------------------------------------------
@shared_task(bind=True, name="src.tasks.fetch_lecture_data")
def fetch_lecture_data(self, task_request: dict) -> str:
    logger.info("Starting fetch_lecture_data with request: %s", task_request)

    lecture_details_by_scholar_responses = get_lecture_details(
        request=LectureDetailsByScholarRequest(**task_request)
    )
    logger.info("Fetched %d lecture records.", len(lecture_details_by_scholar_responses))

    lecture_ids_from_db = get_all_lecture_ids()
    if lecture_ids_from_db:
        db_ids = {d["id"] for d in lecture_ids_from_db}
        before_count = len(lecture_details_by_scholar_responses)
        lecture_details_by_scholar_responses = [
            d for d in lecture_details_by_scholar_responses if d["id"] not in db_ids
        ]
        after_count = len(lecture_details_by_scholar_responses)
        logger.info("Filtered out %d existing lectures; %d remain.", before_count - after_count, after_count)

    signatures = [
        run_pipeline_worker.s(transform_and_validate(lecture_response).model_dump())
        for lecture_response in lecture_details_by_scholar_responses
    ]

    parallel_header = group(signatures)
    callback_task = aggregate_pipeline_results.s()

    workflow_result = chord(parallel_header)(callback_task)

    logger.info("Chord launched with %d worker tasks. Workflow ID: %s", len(signatures), workflow_result.id)
    return f"Workflow submitted: {workflow_result.id}"


# ---------------------------------------------------------
# 1. THE CONSUMER (Parallel Worker Task)
# ---------------------------------------------------------
@shared_task(
    bind=True,
    name="src.tasks.run_pipeline_worker",
    pydantic=True,
    max_retries=3,
    default_retry_delay=60,
    rate_limit="10/m",  # 10 requests per minute across workers
)
def run_pipeline_worker(self, request: PipelineRequest) -> PipelineResponse | None:
    logger.info("Running pipeline worker task: %s", self.request.id)
    try:
        response = run_pipeline(request)
        logger.info("Task %s completed successfully.", self.request.id)
        return response
    except ConnectionError as exc:
        logger.warning(
            "Task %s failed due to connection error. Retrying in %ss (attempt %d).",
            self.request.id,
            self.default_retry_delay,
            self.request.retries + 1,
        )
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error("Task %s failed after maximum retries.", self.request.id)


# ---------------------------------------------------------
# 2. THE CALLBACK (Aggregation/Fan-in Task)
# ---------------------------------------------------------
@shared_task(name="src.tasks.aggregate_pipeline_results")
def aggregate_pipeline_results(results: List[PipelineResponse]):
    logger.info("Aggregating %d pipeline results.", len(results))

    successful_results = [
        result.get("item") for result in results if result.get("item") and result.get("item").get("id")
    ]
    successful_count = len(successful_results)
    failed_count = len(results) - successful_count

    logger.info(
        "Pipeline aggregation complete. Successful: %d | Failed: %d",
        successful_count,
        failed_count,
    )

    db_insert_result = insert_many_items(successful_results)
    if db_insert_result:
        logger.info("Successfully inserted %d results into DB.", successful_count)
    else:
        logger.warning("DB insert failed or returned empty result.")

    summary = {"total": len(results), "successes": successful_count, "failures": failed_count}
    logger.info("Aggregation summary: %s", summary)
    return summary


# ---------------------------------------------------------
# 3. Utility function
# ---------------------------------------------------------
def transform_and_validate(lectureDetailsByScholarResponse: LectureDetailsByScholarResponse) -> PipelineRequest:
    logger.debug("Transforming and validating lecture details: %s", lectureDetailsByScholarResponse.id)
    pipelineRequest = PipelineRequest(
        lecture_details_by_scholar=lectureDetailsByScholarResponse,
        item_id=str(lectureDetailsByScholarResponse.id),
        target_lang_code="en",
        target_lang_name="English",
    )
    return PipelineRequest.model_validate(pipelineRequest)
