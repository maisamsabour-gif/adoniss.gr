FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    curl \
    gettext \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && adduser --system --ingroup app --home /app app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chmod +x /app/deploy/docker/entrypoint.sh && \
    chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["/app/deploy/docker/entrypoint.sh"]
