# Stock Signal Bot - Docker Image
# Build: docker build -t stockbot .
# Run:   docker run -p 8501:8501 stockbot

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY stockbot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY stockbot/ .

# Create reports directory
RUN mkdir -p reports

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
