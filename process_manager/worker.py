import os
from celery import Celery
from celery.schedules import crontab
from ..models.enrichment.Translation import (
    TranslationServiceRequest,
    TranslationServiceResponse,
)

app = Celery("background_tasks", 
             backend=os.getenv("MONGODB_URI",""), 
             broker="pyamqp://guest:guest@localhost:5672//")

@app.task
def test(arg):
    print(arg)


@app.task
def add(x, y):
    z = x + y
    print(z)