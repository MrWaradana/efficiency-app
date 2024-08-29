# Stage 1: Builder
FROM python:3.11-buster as builder

# Install Poetry
RUN pip install poetry

# Set environment variables for Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy pyproject.toml and poetry.lock for dependency installation
COPY pyproject.toml poetry.lock ./

# Install dependencies with Poetry
RUN poetry install --no-dev --no-root

# Stage 2: Runtime
FROM python:3.11-slim-buster as runtime

# Set environment variables for Poetry virtual environment
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app/

# Expose the port on which the application will run
EXPOSE 3002

# Entry point for running the application
ENTRYPOINT ["poetry", "run", "python", "src/server.py"]
