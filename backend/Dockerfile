FROM python:3.12-slim AS builder

WORKDIR /app
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.1

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"
# Copy dependency files
COPY pyproject.toml poetry.lock alembic.ini ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.12-slim

# Copy packages folders
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# Copy source code
COPY . .
RUN chmod +x startup.sh

# Run FastAPI with auto-reload
CMD ["bash", "startup.sh"]