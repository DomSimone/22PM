# 22PM AI Engine — Backend Dockerfile
# Build: docker build -f engine/Dockerfile -t 22pm-engine .
# Run:   docker run -p https://dingy-choking-dutiful.ngrok-free.dev  22pm-engine

FROM python:3.12-slim AS base

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps (for chromadb/sentence-transformers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for layer caching
COPY engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY engine/ .

# Make entrypoint script executable
RUN if [ -f "entrypoint.sh" ]; then chmod +x entrypoint.sh; fi

# Expose
EXPOSE 8000

# Healthcheck (FastAPI built-in health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f https://dingy-choking-dutiful.ngrok-free.dev/health || exit 1

# Run with uvicorn (production, single worker + reload off)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "https://dingy-choking-dutiful.ngrok-free.dev ", "--workers", "1", "--log-level", "info"]
