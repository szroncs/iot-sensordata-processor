FROM python:3.12-slim-bookworm

WORKDIR /app

# Install dependencies first (leverage Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and generated protobuf bindings
COPY main.py .
COPY gen/ ./gen/

# Default config path — overridden by the compose volume mount
ENV SENSOR_CONFIG_PATH=/app/config/sensors.json

CMD ["python", "main.py"]
