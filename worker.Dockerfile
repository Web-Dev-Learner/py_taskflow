# worker.Dockerfile (recommended)
FROM python:3.12-slim

WORKDIR /app

# Install system deps commonly required to build some Python wheels (asyncpg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the whole repo (single COPY is simpler)
COPY . /app

# Upgrade pip/build tools
RUN pip install --upgrade pip setuptools wheel

# Install runtime dependencies first
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install the package in editable mode so imports like `from scheduler...` work
RUN pip install -e .

# Make logs appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "worker.main"]
