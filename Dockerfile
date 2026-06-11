# ── Stage 1: dependencies ─────────────────────────────────────────────────────
FROM python:3.12-slim AS deps

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: final image ──────────────────────────────────────────────────────
FROM python:3.12-slim AS final

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source
COPY main.py .

# Copy the executable — must be present at build time
COPY FindFast.exe .

# Railway injects $PORT at runtime; default to 8000 for local use
ENV PORT=8000

EXPOSE $PORT

# Use gunicorn for production; Railway reads $PORT automatically
CMD ["sh", "-c", "gunicorn main:app --bind 0.0.0.0:${PORT} --workers 2 --timeout 120"]