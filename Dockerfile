# Based on https://docs.astral.sh/uv/guides/integration/docker/#installing-uv

# Stage 1: Build the virtual environment leveraging uv's builder image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Enable bytecode compilation, to improve startup time
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install the project's dependencies using the lockfile and settings
# We use cache mounts to keep the uv cache across docker builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Add the rest of the project source code
COPY . /app

# Sync the project code itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


# Stage 2: Final lightweight runtime image
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy the built virtual environment from the builder stage
# This strips the `uv` toolchain and caches out of the final image
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY . /app

# Place the virtual environment's executables on the PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
