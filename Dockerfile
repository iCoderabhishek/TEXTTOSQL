# Use a lightweight python image
FROM python:3.12-slim-bookworm

# Copy uv from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation and suppress uv's virtualenv warning
ENV UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=1

# Copy project definition files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application
COPY . .

# Expose a default port (cloud providers often use 8080 or dynamically assign PORT)
EXPOSE 8080

# Run the FastAPI server (binds to $PORT if set by the cloud platform, else 8080)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
