from dotenv import load_dotenv
import os
from kombu import Queue, Exchange
load_dotenv()
## Broker settings.
# List of modules to import when the Celery worker starts.
# imports = ("myapp.tasks",)
## Using the database to store task state and results.
# result_backend = 'db+sqlite:///results.db'
# task_annotations = {"tasks.translate": {"rate_limit": "10/m"}}



CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('MONGODB_URI')  # DIFFERENT NAME HERE
CELERY_TIMEZONE = "Asia/Karachi"
CELERY_ENABLE_UTC = True


# Missing: Queue Definitions
CELERY_QUEUES = (
    Queue('producer_queue', Exchange('producer_exchange'), routing_key='producer_key'),
    Queue('pipeline_queue', Exchange('pipeline_exchange'), routing_key='pipeline_key'),
)

# Missing: Routing Definitions
CELERY_ROUTES = {
    # Route scheduled/callback tasks to the faster queue
    'app.fetch_lecture_data': {'queue': 'producer_queue'},
    'app.aggregate_pipeline_results': {'queue': 'producer_queue'},
    # Route heavy tasks to the dedicated queue
    'app.run_pipeline_worker': {'queue': 'pipeline_queue'},
}

CELERY_ROUTES = {
    'app.tasks.fetch_lecture_data': {'queue': 'producer_queue'},
    'app.tasks.run_pipeline_worker': {'queue': 'pipeline_queue'},
    'app.tasks.aggregate_pipeline_results': {'queue': 'producer_queue'},
}

# Missing: Reliability Settings (Highly Recommended)
CELERY_TASK_ACKS_LATE = True