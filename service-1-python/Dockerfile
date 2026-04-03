FROM python:3.12-slim-bookworm

WORKDIR /app

# Install dependencies first (leverage Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY main.py .
COPY gen/ ./gen/

# Setup the entrypoint
CMD ["python", "main.py"]
