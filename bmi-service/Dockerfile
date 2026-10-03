# ── Stage 1: builder ──
# This stage has pip, build tools, and anything needed to INSTALL
# dependencies. None of this ships in the final image.
FROM python:3.12-slim AS builder

WORKDIR /code

COPY requirements.txt .
# Install into a local folder we can copy out, instead of system-wide
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: final runtime image ──
# Fresh, clean base — none of the builder stage's leftover files/cache
FROM python:3.12-slim

# Create a dedicated non-root user and group.
# --system = no login shell, no home dir prompts, built for services.
RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /code

# Copy ONLY the installed packages from the builder stage, not the
# whole builder filesystem
COPY --from=builder /install /usr/local

COPY app ./app

# Switch to the non-root user for everything from here on
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
