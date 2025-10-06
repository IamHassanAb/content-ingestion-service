from celery import shared_task, group, chord
from typing import List
from src.models.pipeline.Pipeline import PipelineRequest, PipelineResponse
from src.models.ingestion.LectureDetailsByScholar import (
    LectureDetailsByScholarRequest,
    LectureDetailsByScholarResponse,
)
from src.services.pipeline import run_pipeline
from src.services.ingestion_service import get_lecture_details
from celery.exceptions import MaxRetriesExceededError
from src.services.redis_service import set_lecture_dto


# 3. THE PRODUCER (Scheduled Task using Chord)
@shared_task(bind=True, name="app.fetch_lecture_data")
def fetch_lecture_data(self, taskRequest: LectureDetailsByScholarRequest) -> str:

    lectureDetailsByScholarResponses = get_lecture_details(request=taskRequest)

    # 1. Create Signatures for the parallel worker tasks
    signatures = [
        run_pipeline_worker.s(transform_and_validate(lecture_response))
        for lecture_response in lectureDetailsByScholarResponses
    ]

    # 2. Define the parallel group (the header of the chord)
    parallel_header = group(signatures)

    # 3. Define the aggregation task (the callback of the chord)
    callback_task = aggregate_pipeline_results.s()

    # 4. Launch the chord: run the header (Group) in parallel, then run the callback
    # The result of this call is the AsyncResult of the *callback* task.
    workflow_result = chord(parallel_header)(callback_task)

    # You can return the result ID for tracking the entire batch
    return f"Workflow submitted: {workflow_result.id}"


# 1. THE CONSUMER (Parallel Worker Task)
# This task executes the heavy-lifting pipeline.
@shared_task(
    bind=True,
    name="app.run_pipeline_worker",
    pydantic=True,
    max_retries=3,  # Retry up to 3 times on failure
    default_retry_delay=60,  # Wait 60 seconds between retries
)
def run_pipeline_worker(self, request: PipelineRequest) -> PipelineResponse | None:
    """Run the ingestion pipeline with built-in retry logic."""
    try:
        # The run_pipeline function is where network/IO errors might occur.
        return run_pipeline(request)
    except ConnectionError as exc:
        # If a transient network error occurs, retry the task.
        try:
            print(
                f"Task {self.request.id} failed, retrying in {self.default_retry_delay}s. Attempt {self.request.retries + 1}"
            )
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            # If maximum retries are hit, log failure and allow task to fail.
            print(f"Task {self.request.id} failed after maximum retries.")


# 2. THE CALLBACK (Aggregation/Fan-in Task)
# This task runs only AFTER all run_pipeline_worker tasks in the Group finish.
@shared_task(name="app.aggregate_pipeline_results")
def aggregate_pipeline_results(results: List[PipelineResponse]):
    """Collects and processes results from all parallel pipeline runs."""
    successful_count = sum(1 for r in results if r.item_id > 0)
    failed_count = len(results) - successful_count

    # In a real app, you would log these results, update a database, or send a final notification.
    # TODO: Add logging and cache update here.
    # Connect to Redis (adjust host/port/db as needed)
    # Store each pipeline result in Redis using item_id as key
    for result in results:
        # add logic to add resutls in cache
        set_lecture_dto(result.to_flat_dict())

    print("\n--- Aggregation Complete ---")
    print(f"Total tasks run: {len(results)}")
    print(f"Successful pipelines: {successful_count}")
    print(f"Failed or permanently retried pipelines: {failed_count}")
    return {"total": len(results), "successes": successful_count}


# Move this in Utils


def transform_and_validate(
    lectureDetailsByScholarResponse: LectureDetailsByScholarResponse,
) -> PipelineRequest:
    pipelineRequest = PipelineRequest(
        lecture_details_by_scholar=lectureDetailsByScholarResponse,
        item_id=str(lectureDetailsByScholarResponse.id),
        target_lang_code="en",
        target_lang_name="English",
    )
    return PipelineRequest.model_validate(pipelineRequest)
