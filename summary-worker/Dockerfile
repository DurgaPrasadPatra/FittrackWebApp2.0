# ── Stage 1: builder ──
FROM python:3.12-slim AS builder

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: final runtime image ──
FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /code

COPY --from=builder /install /usr/local
COPY app ./app

USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
