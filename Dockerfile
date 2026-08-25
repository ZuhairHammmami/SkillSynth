# ============================================================================
# SkillSynth Backend — Multi-stage Dockerfile
# ============================================================================

# --- Stage 1: Build dependencies ---
FROM python:3.14-slim AS builder

WORKDIR /app

# Install build system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.14-slim AS runtime

WORKDIR /app

# Runtime deps only (psycopg2 needs libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/backend /app/src/backend
COPY src/migrations /app/src/migrations
COPY src/migrations_alembic /app/src/migrations_alembic
COPY run.py alembic.ini ./
COPY skillsynth.db /app/skynth.db

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "run.py"]
