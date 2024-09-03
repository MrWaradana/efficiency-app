# Define variables
POETRY = poetry
PYTHON = $(POETRY) run python
APP = src/server.py

# Targets and their rules

# Install dependencies
install:
	$(POETRY) install

# Run the application
run:
	gunicorn -c gunicorn.py main:app

# Run tests
test:
	$(POETRY) run pytest

# Lint the code
lint:
	$(POETRY) run flake8 app core

# Format the code
format:
	$(POETRY) run black core app
	$(POETRY) run isort app core

# Clean up cache and pyc files
clean:
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm -f {} +

# Help target
help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  run        - Run the application"
	@echo "  test       - Run tests"
	@echo "  lint       - Lint the code"
	@echo "  format     - Format the code"
	@echo "  clean      - Clean up cache and pyc files"
	@echo "  help       - Show this help message"

# Default target
.PHONY: install run test lint format clean venv help
default: help
