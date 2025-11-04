# **Step 1 — Project Structure (Recap)**

```
project-root/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── src/
│   ├── main.py           # FastAPI app
│   └── tasks.py          # Celery tasks
└── process_manager/
    └── app.py            # Celery app + beat schedule
```

* `.env` contains:

```env
CELERY_CONFIG_MODULE=process_manager.config
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq_container:5672//
MONGODB_URI=mongodb://mongodb_container:27017/
```

> Replace `rabbitmq_container` and `mongodb_container` with **your existing container names**.

---

# **Step 2 — Dockerfile (Reusable for FastAPI and Celery)**

```dockerfile
# Base Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Unbuffered logs
ENV PYTHONUNBUFFERED=1

# Default command (fallback, overridden in Compose)
CMD ["python", "main.py"]
```

* Use `WORKDIR /app` so it matches your Compose volume mount for live reload.
* CMD is just a fallback; Compose will override it.

---

# **Step 3 — docker-compose.yml**

```yaml
version: "3.9"

services:

  fastapi_app:
    build: .
    container_name: fastapi_app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    env_file:
      - .env
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    networks:
      - balagh_network

  celery_worker:
    build: .
    container_name: run_pipeline_worker
    command: celery -A process_manager.app worker -l info
    env_file:
      - .env
    volumes:
      - .:/app
    networks:
      - balagh_network

  celery_beat:
    build: .
    container_name: fetch_lectures_beat
    command: celery -A process_manager.app beat -l info
    env_file:
      - .env
    volumes:
      - .:/app
    networks:
      - balagh_network

  flower:
    image: mher/flower:2.0.1
    container_name: celery_flower
    command: >
      flower --broker=amqp://guest:guest@rabbitmq_container:5672// --port=5555
    ports:
      - "5555:5555"
    networks:
      - balagh_network

networks:
  balagh_network:
    external: true
    name: bridge  # Replace with the network your existing RabbitMQ/MongoDB containers are on
```

**Notes:**

* `depends_on` is removed for RabbitMQ/MongoDB since they are external.
* Volume mount allows **FastAPI live reload**.
* All services are on the **same network** as RabbitMQ/MongoDB.

---

# **Step 4 — Start the system**

1. Make sure **RabbitMQ and MongoDB containers are running**.
2. From project root:

```bash
docker compose up --build
docker compose build --no-cache (for building from scratch)
docker compose build (use cache to reuse some stuff for build)
```

* FastAPI: [http://localhost:8000](http://localhost:8000)
* Flower: [http://localhost:5555](http://localhost:5555)

> Celery Worker and Beat logs will show task execution and scheduling.

---

# **Step 5 — Scale workers (optional)**

```bash
docker compose up --scale celery_worker=3
```

* Starts **3 worker containers** for horizontal scaling.
* Beat remains **single instance**.

---

# **Step 6 — Stop the system**

```bash
docker compose stop
```

* Stops all containers defined in your Compose file without removing them.

---

# **Step 7 — Remove containers, networks, volumes**

```bash
docker compose down
```

* Stops and removes all containers, networks created by Compose.

* Does **not touch your external RabbitMQ/MongoDB** since they are not defined in Compose.

* To remove **all volumes** (if you had any local volumes):

```bash
docker compose down -v
```

---

# ✅ Summary of Flow

1. FastAPI pushes tasks → RabbitMQ
2. Celery Workers consume tasks → store results in MongoDB
3. Celery Beat schedules tasks → RabbitMQ → Workers
4. Flower monitors tasks via RabbitMQ
5. All services communicate via the **same Docker network**