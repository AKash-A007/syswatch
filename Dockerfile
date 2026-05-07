# ─────────────────────────────────────────────────────────────────────────────
# SysWatch Pro — Multi-Stage Dockerfile (FastAPI Backend only)
#
# Stage 1 (builder): Install all Python deps into a virtual env
# Stage 2 (runtime): Copy only the venv + src/backend — slim final image
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better layer caching)
COPY requirements.txt .

# Install into an isolated venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="SysWatch Pro Backend"
LABEL org.opencontainers.image.description="FastAPI backend for SysWatch Pro monitoring system"
LABEL org.opencontainers.image.source="https://github.com/AKash-A007/syswatch"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy the venv from builder (no build tools in final image)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only the backend source code
COPY src/backend/ ./backend/
COPY src/utils/ ./utils/
COPY src/agent/ ./agent/

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the FastAPI backend with uvicorn
CMD ["uvicorn", "backend.api_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
