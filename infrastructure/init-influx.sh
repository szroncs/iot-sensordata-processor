#!/bin/bash
set -e

echo "Creating invalid_data bucket for telemetry..."

# Wait for InfluxDB to start if needed, but the init scripts run when it's ready.
influx bucket create \
  -n invalid_data \
  -o T4PIJ6_org \
  -t my-super-secret-auth-token \
  -r 7d

echo "Initialization complete."
