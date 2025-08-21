# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# If you don't build any native deps, you can delete build-essential
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt is in the repo root (build context), so copy from there
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy just the source tree
COPY src/ /app/src

# (Optional) if you later add other top-level runtime files, copy them explicitly:
# COPY scripts/ /app/scripts

# Non-root user for safety
RUN useradd -m appuser \
 && chown -R appuser:appuser /app
USER appuser

# Default command (adjust if your entry point differs)
CMD ["python", "src/main.py"]