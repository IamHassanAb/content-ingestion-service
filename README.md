# Content Ingestion Service

> **Intelligent data pipeline for extracting, enriching, and processing educational content at scale**

A production-ready FastAPI service that automates the ingestion, translation, and enrichment of lecture data. Built with distributed task processing, real-time APIs, and robust data persistence.

---

## 🎯 Overview

The Content Ingestion Service is designed to:

- **Ingest** lecture/educational content from external sources (paginated APIs)
- **Enrich** metadata with translations and AI-powered tagging
- **Process** data through a flexible pipeline architecture
- **Scale** horizontally with Celery workers handling parallel processing
- **Persist** all data in MongoDB with clean schemas

### Key Use Cases

- 🎓 **Educational Platforms**: Batch import and enrich course/lecture content
- 🌍 **Multilingual Content**: Automatic translation and localization of materials
- 🏗️ **Data Pipelines**: Integration point for ETL workflows with Airflow/Dagster
- 📊 **Content Analysis**: Extract metadata, tags, and enriched attributes at scale

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Background Jobs & Scheduling](#-background-jobs--scheduling)
- [Database Schema](#-database-schema)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd content-ingestion-service

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services (FastAPI, Celery Workers, Celery Beat Scheduler)
docker compose up --build

# Services available:
# - FastAPI API:     http://localhost:8000
# - API Docs:        http://localhost:8000/docs
# - Flower Monitor:  http://localhost:5555
```

**Prerequisites:**
- Docker & Docker Compose
- RabbitMQ and MongoDB containers running on the same network
- Network named `balagh_network` (or adjust in docker-compose.yml)

### Local Development (Python 3.11+)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing & development

# Configure environment
cp .env.example .env
# Edit .env

# Start RabbitMQ and MongoDB (ensure they're running)
# Then start FastAPI:
uvicorn src.main:app --reload --port 8000

# In a separate terminal, start Celery Worker:
celery -A process_manager.app worker -l info

# In another terminal, start Celery Beat (scheduler):
celery -A process_manager.app beat -l info

# Monitor tasks with Flower (optional):
celery -A process_manager.app -b amqp://guest:guest@localhost:5672// flower --port=5555
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Service                         │
│                    (HTTP API, Endpoints)                        │
└────────────────┬───────────────────────────────────────────────┘
                 │
         ┌───────┴──────────┐
         ▼                  ▼
    ┌─────────────┐    ┌─────────────┐
    │  RabbitMQ   │◄───┤ Celery Beat │
    │  (Broker)   │    │ (Scheduler) │
    └──────┬──────┘    └─────────────┘
           │
      ┌────┴─────────────────┐
      ▼                      ▼
  ┌────────────┐         ┌────────────┐
  │  Worker 1  │ ....... │  Worker N  │
  │ (Parallel  │         │ (Parallel  │
  │  Tasks)    │         │  Tasks)    │
  └─────┬──────┘         └─────┬──────┘
        │                      │
        └──────────┬───────────┘
                   ▼
            ┌─────────────────┐
            │   MongoDB       │
            │  (Persistent    │
            │   Storage)      │
            └─────────────────┘
```

### Component Breakdown

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Server** | FastAPI + Uvicorn | REST endpoints for data ingestion, enrichment, pipeline execution |
| **Task Broker** | RabbitMQ | Message queue for task distribution |
| **Task Scheduler** | Celery Beat | Periodic task scheduling (e.g., scheduled fetches) |
| **Workers** | Celery | Parallel processing of background jobs |
| **Data Store** | MongoDB | Persistent storage of ingested and processed data |
| **Cache** | Redis | Caching and rate limiting |
| **Monitoring** | Flower | Task execution monitoring and visualization |

---

## 📦 Installation

### Prerequisites

- **Python 3.11+** (for local development)
- **Docker & Docker Compose** (for containerized setup)
- **RabbitMQ** container running
- **MongoDB** container running
- **Redis** container (optional, for advanced caching)

### Step 1: Clone & Setup

```bash
git clone <repository-url>
cd content-ingestion-service
```

### Step 2: Create Environment File

```bash
cat > .env << EOF
# FastAPI
FASTAPI_ENV=development

# Celery Configuration
CELERY_CONFIG_MODULE=process_manager.config
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq_container:5672//
CELERY_RESULT_BACKEND=mongodb://mongodb_container:27017/celery_results

# MongoDB
MONGODB_URI=mongodb://mongodb_container:27017/
MONGO_DB_NAME=content_ingestion

# Redis (Optional)
REDIS_URL=redis://redis_container:6379/0

# External APIs
TRANSLATION_API_KEY=your_translation_api_key
LLM_API_KEY=your_groq_api_key
EOF
```

> Replace container names with your actual RabbitMQ/MongoDB container names.

### Step 3: Install Dependencies

**Docker:**
```bash
docker compose build
docker compose up
```

**Local:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CELERY_BROKER_URL` | - | RabbitMQ connection string (AMQP protocol) |
| `CELERY_RESULT_BACKEND` | - | MongoDB connection for task results |
| `MONGODB_URI` | `mongodb://localhost:27017/` | MongoDB connection URL |
| `MONGO_DB_NAME` | `content_ingestion` | Database name for ingested data |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection (optional) |
| `TRANSLATION_API_KEY` | - | API key for translation service (Groq) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Celery Schedule Configuration

Edit [process_manager/app.py](process_manager/app.py) to modify scheduled tasks:

```python
celery_app.conf.beat_schedule = {
    "fetch-lectures": {
        "task": "src.tasks.fetch_lecture_data",
        "schedule": crontab(minute='*/1'),  # Every 1 minute
        "kwargs": {
            "task_request": {
                "Page": 1,
                "PageSize": 1000,
                "ScholarId": 146
            }
        },
    },
}
```

---

## 📡 API Documentation

### Interactive API Docs

Once the service is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Overview

#### 1. **Ingest Endpoint** — Fetch lecture data

```http
GET /ingest/lecture-details?page=1&page_size=100&scholar_id=146
```

**Purpose**: Fetch paginated lecture data from external source

**Query Parameters**:
- `page` (int): Page number
- `page_size` (int): Records per page
- `scholar_id` (int): Scholar identifier

**Response**:
```json
[
  {
    "id": "lecture-001",
    "title": "Introduction to Machine Learning",
    "description": "...",
    "scholar_id": 146,
    "created_at": "2026-02-21T10:30:00Z"
  }
]
```

#### 2. **Enrichment Endpoints** — Add metadata and translations

```http
POST /enrich/enrich-metadata
Content-Type: application/json

{
  "item_id": "lecture-001",
  "content": "Introduction to Machine Learning",
  "language": "en"
}
```

**Response**:
```json
{
  "item_id": "lecture-001",
  "tags": ["machine-learning", "ai", "data-science"],
  "metadata": {
    "language": "en",
    "detected_category": "Technology"
  }
}
```

```http
POST /enrich/get-translation
Content-Type: application/json

{
  "text": "Introduction to Machine Learning",
  "source_language": "en",
  "target_language": "es"
}
```

**Response**:
```json
{
  "original_text": "Introduction to Machine Learning",
  "translated_text": "Introducción al aprendizaje automático",
  "source_language": "en",
  "target_language": "es"
}
```

#### 3. **Pipeline Endpoint** — Execute full processing pipeline

```http
POST /pipeline/execute
Content-Type: application/json

{
  "item_id": "lecture-001",
  "content": "...",
  "operations": ["translate", "enrich", "validate"]
}
```

**Response**:
```json
{
  "item_id": "lecture-001",
  "status": "success",
  "results": {
    "translated": true,
    "enriched": true,
    "validated": true
  }
}
```

---

## 🔄 Background Jobs & Scheduling

### Scheduled Tasks (Celery Beat)

Celery Beat runs scheduled tasks based on the configuration in [process_manager/app.py](process_manager/app.py).

#### Task: `fetch_lecture_data`

**When**: Runs on schedule (default: every 1 minute, configured in Celery Beat)

**What it does**:
1. Fetches lecture data from external API with given parameters
2. Filters out lectures already in MongoDB
3. Creates parallel worker tasks for new lectures
4. Aggregates results

**Example trigger**:
```bash
# Manually trigger (for testing):
celery -A process_manager.app call src.tasks.fetch_lecture_data --args='{"Page": 1, "PageSize": 100, "ScholarId": 146}'
```

### Worker Tasks (Celery Workers)

Workers pick up tasks from RabbitMQ and execute them in parallel.

#### Task: `run_pipeline_worker`

Processes individual lecture records through the enrichment pipeline:
- Translates content
- Extracts and enriches metadata
- Validates data
- Stores results in MongoDB

### Monitoring Tasks

Use **Flower** to monitor task execution:

```bash
# Access Flower dashboard
http://localhost:5555

# View:
# - Active tasks
# - Task history
# - Worker status
# - Task execution times
```

**CLI monitoring**:
```bash
# Celery status
celery -A process_manager.app inspect active
celery -A process_manager.app inspect stats
celery -A process_manager.app inspect registered
```

---

## 💾 Database Schema

### MongoDB Collections

#### `lectures_raw`
Raw ingested lecture data

```json
{
  "_id": ObjectId,
  "id": "lecture-001",
  "title": "Introduction to Machine Learning",
  "description": "...",
  "scholar_id": 146,
  "content": "...",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### `lectures_enriched`
Processed and enriched data

```json
{
  "_id": ObjectId,
  "item_id": "lecture-001",
  "original_title": "Introduction to Machine Learning",
  "translated_title": "Introducción al aprendizaje automático",
  "tags": ["machine-learning", "ai", "data-science"],
  "metadata": {
    "language": "en",
    "category": "Technology",
    "sentiment": "neutral"
  },
  "translations": {
    "es": "...",
    "fr": "..."
  },
  "pipeline_status": "completed",
  "processed_at": ISODate
}
```

---

## 👨‍💻 Development

### Project Structure

```
content-ingestion-service/
├── src/                          # Main application code
│   ├── main.py                  # FastAPI application entry point
│   ├── tasks.py                 # Celery task definitions
│   ├── api/                     # API endpoints
│   │   └── v1/endpoints/
│   │       ├── ingestion.py     # Ingest endpoints
│   │       ├── enrichment.py    # Enrichment endpoints
│   │       └── pipeline.py      # Pipeline endpoints
│   ├── services/                # Business logic
│   │   ├── ingestion_service.py
│   │   ├── enrichment_service.py
│   │   └── pipeline.py
│   ├── models/                  # Data models & schemas
│   ├── repository/              # Database access layer
│   ├── llm/                     # LLM integrations (Groq)
│   ├── messaging/               # Kafka producer setup
│   └── utils/                   # Utilities (logging, rate limiting, etc.)
├── process_manager/             # Celery configuration
│   ├── app.py                   # Celery app & Beat schedule
│   ├── config.py                # Celery configuration
│   ├── worker.py                # Worker entry point
│   └── jobs.py                  # Job definitions
├── tests/                       # Unit & integration tests
├── docker-compose.yml           # Multi-container orchestration
├── Dockerfile                   # Container image
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/app/services/test_enrichment_service.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** and test locally:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   pytest
   ```

3. **Run linting & formatting**:
   ```bash
   black src/
   flake8 src/
   mypy src/
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** with test results attached

---

## 🐛 Troubleshooting

### Common Issues

#### **1. ModuleNotFoundError: No module named 'src'**

**Cause**: Python path not configured correctly in container or terminal

**Solution**:
```bash
# For local development, run from project root:
cd content-ingestion-service
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# For Docker, ensure COPY . . is in Dockerfile
```

#### **2. Celery Worker Cannot Connect to RabbitMQ**

**Error**: `Connection refused` or `Could not connect to broker`

**Solution**:
```bash
# Verify RabbitMQ is running
docker ps | grep rabbitmq

# Check CELERY_BROKER_URL in .env
# Format: amqp://username:password@host:port//

# Test connection
amqp-consume-tool -u amqp://guest:guest@localhost:5672// 

# Common issue: container name mismatch
# Update .env to use correct container name or IP
```

#### **3. MongoDB Connection Timeout**

**Error**: `Timeout connecting to MongoDB`

**Solution**:
```bash
# Verify MongoDB container is running
docker ps | grep mongodb

# Check MONGODB_URI in .env
# Format: mongodb://username:password@host:port/

# Test connection with mongosh
mongosh "mongodb://localhost:27017"
```

#### **4. Flower Cannot Find Celery App**

**Error**: `ModuleNotFoundError` in Flower

**Solution**: Ensure Flower command includes correct `-A` parameter:
```bash
celery -A process_manager.app flower --port=5555
```

#### **5. Tasks Not Running on Schedule**

**Debug**:
```bash
# Check Celery Beat logs
docker logs fetch_lectures_beat

# Verify schedule configuration in process_manager/app.py
# Check crontab syntax: https://crontab.guru

# Verify worker is consuming tasks
docker logs run_pipeline_worker
```

**See [issues-faced-cause-resolution.md](issues-faced-cause-resolution.md) for detailed resolution guide.**

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Before Contributing

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch

### Development Guidelines

- Write clear commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
- Add tests for new features
- Ensure all tests pass: `pytest`
- Follow PEP 8 code style
- Update documentation for API changes

### Submitting Changes

1. **Push** to your fork
2. **Create** a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Test results / coverage report
3. **Wait** for code review
4. **Address** feedback and merge!

### Reporting Issues

Found a bug? Please report it on GitHub Issues with:
- Clear title and description
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- **Documentation**: See [decision_flow.md](decision_flow.md) for architecture details and [steps-to-setup-teardown.md](steps-to-setup-teardown.md) for deployment guide
- **Issues**: Report on GitHub Issues
- **Questions**: Create a GitHub Discussion or contact the team

---

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Flower Monitoring](https://flower.readthedocs.io/)

---

**Last Updated**: February 2026  
**Status**: Active Development (Beta)
