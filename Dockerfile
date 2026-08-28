FROM python:3.11-slim

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements-ai.txt .
RUN pip install --no-cache-dir -r requirements-ai.txt

# Copy application source code
COPY . .

# Pre-train / verify all 6 AI model artifacts during image build
RUN python -c "from ai_service import ensure_models; ensure_models()"

# Expose default port
EXPOSE 10000

ENV PORT=10000
ENV PYTHONUNBUFFERED=1

# Use dynamic $PORT assigned by Render or default to 10000
CMD ["sh", "-c", "uvicorn ai_service:app --host 0.0.0.0 --port ${PORT:-10000}"]
