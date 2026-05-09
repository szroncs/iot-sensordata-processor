FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY views/ ./views/

ENV SENSOR_CONFIG_PATH=/app/config/sensors.json
ENV ADMIN_HOST=0.0.0.0
ENV ADMIN_PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
