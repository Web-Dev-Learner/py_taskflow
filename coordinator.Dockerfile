# coordinator.Dockerfile (replace your current file)
FROM python:3.12-slim

WORKDIR /app

# Install system build deps needed by some wheels (asyncpg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the repo into the image (single COPY is simpler & reliable)
COPY . /app

# Ensure pip/build tools are recent
RUN pip install --upgrade pip setuptools wheel

# Install runtime dependencies first (good cache behavior)
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install project package (editable) so imports like `from scheduler...` work
RUN pip install -e .

# Helpful for logs in Docker
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "coordinator.main"]
