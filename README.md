# IoT telemetry optimization: binary serialization and middleware-based sensor data validation

## Project structure

```text
.
├── config
│   └── sensors.json
├── generate_protos.sh
├── infrastructure
│   ├── grafana
│   │   ├── dashboards
│   │   └── provisioning
│   ├── init-influx.sh
│   └── mosquitto.conf
├── PLAN.md
├── podman-compose.yaml
├── proto
│   ├── buf.yaml
│   └── sensor.proto
├── README.md
├── sensor-admin
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── tests
│   │   ├── __init__.py
│   │   └── test_admin.py
│   └── views
│       ├── index.tpl
│       └── sensor_form.tpl
├── service-1-python
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── test_main.py
└── service-2-go
    ├── config.go
    ├── Dockerfile
    ├── go.mod
    ├── go.sum
    ├── main.go
    └── pkg
        ├── middleware
        └── storage
```

## Tech stack

### Python
Generate mock sensor data and publish to MQTT broker.

Sensor types:
- Temperature (Industrial RTD Range: -200 C to 850 C) --> MQTT QoS 0
- Humidity (Industrial humidity typically covers 0 to 100% RH) --> MQTT QoS 1
- CO2 (ppm range: 0-50,000 ppm) --> MQTT QoS 1
- LPG (typically detects gas concentrations in the range of 200-10,000 ppm) --> MQTT QoS 1
- Door (Open/Closed) --> MQTT QoS 1
- Alert (Info, Warning, Critical) --> MQTT QoS 2

### Go
Subscribe to MQTT broker, validate the sensor data, and store it in InfluxDB. Use middleware to validate the sensor data. Use gorutine to handle sensor data parallelly.

Validation per sensor type:
- Temperature: min -2 C to max 82 C
- Humidity: min 15% to max 73% RH
- CO2: min 0 ppm to max 2000 ppm
- LPG: max 800 ppm
- Door: Open/Closed
- Alert: Info, Warning, Critical

### ProtoBuf


### MQTT - mosquitto


### InfluxDB


### Grafana


### Podman


# man:

1. Bring up the whole pod using the podman-compose.yaml:
\`\`\`sh
podman-compose up --build -d
\`\`\`
2. Go subscriber logs:
\`\`\`sh
podman-compose logs -f service-2-go
\`\`\`
3. To watch the Python backend serialize the data into Protocol Buffers and publish them with the assigned QoS flags, tail its logs:
\`\`\`sh
podman-compose logs -f service-1-python
\`\`\`
