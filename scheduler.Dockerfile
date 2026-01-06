# scheduler.Dockerfile (recommended)
FROM python:3.12-slim

WORKDIR /app

# Install system deps commonly required to build some Python wheels (asyncpg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev wget \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Upgrade pip/build tools
RUN pip install --upgrade pip setuptools wheel

# Install Python deps
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install package in editable mode so imports like `from scheduler...` work
RUN pip install -e .

# Make logs appear immediately
ENV PYTHONUNBUFFERED=1

# Expose the port (for documentation; actual port can be controlled by env)
EXPOSE 8000

# Use PORT env if provided (works locally and on Render)
CMD ["sh", "-c", "uvicorn scheduler.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
