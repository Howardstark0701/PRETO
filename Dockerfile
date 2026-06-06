# PRETO — Multi-stage Dockerfile
# Stage 1: Build React frontend
# Stage 2: Build Python deps
# Stage 3: Production image

# ── Stage 1: Frontend build ────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci --silent

COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python deps ───────────────────────────────────────────────────
FROM python:3.10-slim AS py-builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 3: Production image ──────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python packages
COPY --from=py-builder /root/.local /root/.local

# App source
COPY . .

# Frontend build output → serve as static files
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create non-root user
RUN useradd -m -u 1000 preto && \
    chown -R preto:preto /app

USER preto

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "main.py"]
