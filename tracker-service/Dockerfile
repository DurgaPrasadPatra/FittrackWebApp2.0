# ── Stage 1: builder ──
FROM python:3.12-slim AS builder

WORKDIR /code

# Build tools needed ONLY to compile psycopg2-binary's dependencies.
# These never appear in the final image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: final runtime image ──
FROM python:3.12-slim

# psycopg2 needs libpq (the Postgres client library) at RUNTIME too,
# just not the full -dev/compiler toolchain. This is much smaller.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /code

COPY --from=builder /install /usr/local
COPY app ./app

USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
