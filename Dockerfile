# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim as builder

# Install Poetry
RUN pip install poetry

# Set environment variables for Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set the working directory
WORKDIR /app

# Copy the Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-root

# Use a new slim image for the runtime
FROM python:3.11-slim as runtime

# Set environment variables for Poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy Poetry installation from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application files
COPY . /app/

# Expose port for the application
EXPOSE 3002

# Set the working directory
WORKDIR /app

# Entry point for the application
ENTRYPOINT ["poetry", "run", "python", "src/server.py"]
