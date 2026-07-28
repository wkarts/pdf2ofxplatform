ARG PYTHON_BASE_IMAGE=python:3.13-slim-bookworm
FROM ${PYTHON_BASE_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ghostscript \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

COPY services/converter/pyproject.toml ./
COPY services/converter/src ./src
RUN pip install --upgrade pip \
    && pip install .

RUN useradd --create-home --uid 10001 app \
    && mkdir -p /data/jobs /tmp/pdf2ofx \
    && chown -R app:app /data/jobs /tmp/pdf2ofx /app

USER app
EXPOSE 8000
CMD ["uvicorn", "pdf2ofx.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS test
USER root
COPY services/converter/tests ./tests
RUN pip install ".[dev]" \
    && chown -R app:app /app
USER app
CMD ["pytest", "-q"]
