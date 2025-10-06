from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
load_dotenv()

celery_app = Celery("data_pipeline_process_manager")

celery_app.config_from_envvar("CELERY_CONFIG_MODULE")
celery_app.autodiscover_tasks(["src"])


# ------------------------------
# Celery Beat (Scheduler) Config
# ------------------------------
celery_app.conf.beat_schedule = {
    # Runs every 30 seconds
    # "print-hello-every-30s": {
    #     "task": "app.tasks.say_hello",
    #     "schedule": 30.0,
    #     "args": ("FastAPI Developer",),
    # },
    # Example: run daily at 8 AM
    "fetch-lectures": {
        "task": "src.tasks.fetch_lecture_data",
        "schedule": crontab(minute='*/1'),
        "kwargs": {"taskRequest": {"Page": 1, "PageSize": 1000, "ScholarId": 146}},
    },
}


# from celery import Celery


# # RabbitMQ is used as the Broker (AMQP port 5672 is standard)
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# # MongoDB is used as the Result Backend
# BACKEND_URL = 'mongodb://localhost:27017/celery_results'

# app = Celery(
#     'data_pipeline_project',
#     broker=BROKER_URL,
#     backend=BACKEND_URL,
#     include=['app.tasks']
# )

# # 1. Define custom queues for isolation [9]
# app.conf.task_queues = (
#     # Queue for the scheduling producer (fetch_lecture_data)
#     Queue('producer_queue', Exchange('producer_exchange'), routing_key='producer_key'),
#     # Queue for the parallel, heavy pipeline workers [9]
#     Queue('pipeline_queue', Exchange('pipeline_exchange'), routing_key='pipeline_key'),
# )

# # 2. Configure routing to direct tasks to the appropriate queue [11]
# app.conf.task_routes = {
#     'app.fetch_lecture_data': {'queue': 'producer_queue'}, # High priority/quick scheduling
#     'app.run_pipeline_worker': {'queue': 'pipeline_queue'}, # Heavy lifting
#     'app.aggregate_pipeline_results': {'queue': 'producer_queue'}, # Callback task
# }

# # General configuration settings
# app.conf.update(
#     # Results will expire after 1 hour (3600 seconds) [12]
#     result_expires=3600,
#     # Celery Beat uses UTC by default, ensure timezone is specified [13]
#     timezone='UTC',
#     # Enable late acknowledgment for reliability (task is ack'd only after it succeeds) [14, 15]
#     task_acks_late=True,
#     # Configure serializer for results, matching MongoDB compatibility (default JSON is fine) [16]
#     result_serializer='json',
# )
