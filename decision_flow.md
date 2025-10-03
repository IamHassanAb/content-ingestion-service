
### High-Level Architecture
               ┌─────────────────────────────┐
               │  Scheduler (Airflow/Dagster)│
               │  - Runs /get-data job       │
               │  - Every N min/hrs/week     │
               └───────────────┬─────────────┘
                               │
                               ▼
                 ┌─────────────────────────┐
                 │    Your Service         │
                 │  fetch /get-data items  │
                 │  push IDs → Redis Queue │
                 └───────────────┬─────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               │                                   │
       ┌───────────────┐                   ┌───────────────┐
       │ Worker 1      │                   │ Worker N      │
       │ - Pull from   │                   │ - Pull from   │
       │   Redis queue │                   │   Redis queue │
       │ - Call /trans │                   │ - Call /trans │
       └──────┬────────┘                   └──────┬────────┘
              │                                   │
              ▼                                   ▼
      ┌──────────────────┐              ┌──────────────────┐
      │ External API     │              │ External API     │
      │ /translate       │   ...586...  │ /translate       │
      └──────────────────┘              └──────────────────┘





---
### Decision Framework for /get-data Scheduling
                   ┌───────────────────────────────────┐
                   │ How often does data actually      │
                   │ change at the provider side?      │
                   └───────────────────┬───────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            │                                                     │
       "Frequently" (minutes/hours)                      "Rarely" (days/weeks)
            │                                                     │
   ┌────────▼────────┐                                 ┌──────────▼──────────┐
   │ Do you need near│                                 │ Do you need near-   │
   │ real-time data? │                                 │ real-time updates?  │
   └───────┬─────────┘                                 └──────────┬──────────┘
           │ Yes                                                  │ No
           ▼                                                      ▼
 ┌────────────────────┐                                  ┌────────────────────┐
 │ Poll `/get-data`   │                                  │ Poll `/get-data`   │
 │ often (hourly or   │                                  │ infrequently (e.g. │
 │ faster), OR push   │                                  │ once per day/week) │
 │ for event-driven   │                                  │ Compare against    │
 │ updates if possible│                                  │ stored snapshot.   │
 └────────────────────┘                                  └────────────────────┘
           │                                                       │
           ▼                                                       ▼
  ┌────────────────────┐                                  ┌────────────────────┐
  │ Compare new list   │                                  │ Enqueue only new   │
  │ with cached list.  │                                  │ items for          │
  │ Enqueue only new   │                                  │ translation.       │
  │ or changed items.  │                                  └────────────────────┘
  └────────────────────┘




---
### Flowchart: FastAPI + Celery Beat + RabbitMQ + Workers

                   ┌───────────────────────────────┐
                   │      Consumer / Client        │
                   │ - Calls FastAPI endpoints     │
                   │   (e.g., GET /translations)  │
                   └─────────────┬─────────────────┘
                                 │
                                 ▼
                     ┌─────────────────────────┐
                     │     FastAPI Service      │
                     │ - Exposes endpoints      │
                     │ - Reads from DB / cache │
                     │ - Optional endpoint:     │
                     │   trigger fetch manually │
                     └─────────────┬───────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │       DB / Cache        │
                     │ - Stores translation    │
                     │   results               │
                     │ - Tracks processed IDs  │
                     └─────────────┬───────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │    Celery Workers       │
                     │ - Pull item_id from     │
                     │   RabbitMQ queue       │
                     │ - Call /translate API  │
                     │ - Store results in DB  │
                     │ - Retry failed tasks   │
                     │ - Rate-limited to avoid│
                     │   overwhelming API     │
                     └─────────────┬───────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │   RabbitMQ Queue        │
                     │ - Stores tasks for each │
                     │   item_id               │
                     └─────────────┬───────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │     Celery Beat         │
                     │ - Scheduler (internal) │
                     │ - Triggers fetch_get_data│
                     │   periodically         │
                     │ - Pushes new items to  │
                     │   RabbitMQ queue       │
                     └─────────────────────────┘




### Flowchart: New Architecutre Plan 

               ┌─────────────────────────────┐
               │  Scheduler (Airflow/Celery) │
               │  - Runs get_lecture_details │
               │  - Every weekend            │
               └───────────────┬─────────────┘
                               │
                               ▼
                 ┌─────────────────────────────┐
                 │ FastAPI Service / Collector │
                 │ - Calls get_lecture_details │
                 │ - Stores raw data in Mongo  │
                 │ - Enqueues NEW item_ids →   │
                 │   RabbitMQ queue            │
                 └───────────────┬─────────────┘
                                 │
               ┌─────────────────┴──────────────────┐
               │                                    │
       ┌───────────────┐                    ┌───────────────┐
       │ Worker 1      │                    │ Worker N      │
       │ - Pull item_id│                    │ - Pull item_id│
       │   from queue  │                    │   from queue  │
       │ - translate_text()                 │ - translate_text()
       │ - merge enriched data              │ - merge enriched data
       │   with Mongo record                │   with Mongo record
       │ - insert into "lectures_trans"     │ - insert into "lectures_trans"
       └────────────────┬───────────────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ MongoDB Database   │
              │ - Collection:      │
              │   lectures_raw     │
              │   (fetched weekly) │
              │ - Collection:      │
              │   lectures_trans   │
              │   (translated &    │
              │    enriched data)  │
              └────────────────────┘





