# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only application code now (excludes .venv, cache, logs via .dockerignore)
COPY . .

# Make Python output immediately visible
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8888"]
