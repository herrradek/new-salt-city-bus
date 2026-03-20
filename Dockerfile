# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Install Python deps
FROM python:3.12-slim AS backend-builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 3: Final image
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=backend-builder /install /usr/local
COPY backend/ backend/
COPY --from=frontend-builder /app/frontend/dist frontend/dist

# Create writable data dir for GTFS downloads
RUN mkdir -p backend/app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 10000
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}
