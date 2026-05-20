# IoT telemetry optimization: binary serialization and middleware-based sensor data validation

A full-stack IoT data processing pipeline featuring binary serialization (Protocol Buffers), real-time validation, and automated visualization.

## Architecture

1.  **sensor-admin**: A web-based management interface used to define and configure sensors in `sensors.json`.
2.  **service-1-python**: A sensor simulator that reads the configuration, generates mock telemetry, serializes it using **Protobuf**, and publishes it to **MQTT**.
3.  **MQTT (Mosquitto)**: Acts as the message broker for asynchronous communication.
4.  **service-2-go**: A high-performance subscriber that (validate)s incoming Protobuf messages using a **middleware pipeline** and stores them in **InfluxDB**.
5.  **InfluxDB**: Time-series database storing both valid (raw) and invalid telemetry.
6.  **Grafana**: Visualization platform pre-configured with dashboards to monitor the sensor data.

---

## Project Structure

```text
.
├── config
│   └── sensors.json             # Shared sensor configuration
├── generate_protos.sh           # Script to compile .proto files
├── infrastructure
│   ├── grafana                  # Provisioning and dashboards
│   ├── init-influx.sh           # InfluxDB initialization script
│   └── mosquitto.conf           # MQTT broker configuration
├── podman-compose.yaml          # Container orchestration
├── proto
│   ├── buf.yaml
│   └── sensor.proto             # Protobuf definitions
├── sensor-admin                 # Python (Bottle) management UI
├── service-1-python             # Python sensor simulator
└── service-2-go                 # Go telemetry processor
```

---

## Tech Stack

-   **Languages**: Python 3.11+, Go 1.22+
-   **Serialization**: Protocol Buffers (proto3)
-   **Messaging**: MQTT (QoS 0, 1, and 2 supported)
-   **Storage**: InfluxDB 2.0
-   **Visualization**: Grafana
-   **Infrastructure**: Podman / Docker Compose

---

## Validation Rules (service-2-go)

Telemetery is validated against these operational limits. Data outside these ranges is stored in a separate `invalid_data` bucket.

| Sensor Type | Operational Range |
| :--- | :--- |
| **Temperature** | 10.0°C to 28.0°C |
| **Humidity** | 35.0% to 65.0% RH |
| **CO2** | 0 to 1800 ppm |
| **LPG** | 0 to 1100 ppm |
| **Door** | Boolean (Open/Closed) |
| **Alert** | Severity levels: INFO, WARNING, CRITICAL |

---

## Getting Started

### 1. Build and Run the Stack

Bring up all services (Mosquitto, InfluxDB, Grafana, Admin UI, Simulator, and Processor):

```bash
podman-compose up --build -d
```

### 2. Access Interfaces

-   **Sensor Admin UI**: [http://localhost:8080](http://localhost:8080)
    -   Use this to add, edit, or delete sensors. Click "Apply" to save changes to the shared config.
-   **Grafana Dashboards**: [http://localhost:3000](http://localhost:3000)
    -   Anonymous access is enabled. Go to "Dashboards" -> "Sensor Telemetry" to view real-time data.

---

## Development

### Protobuf Compilation

If you modify `proto/sensor.proto`, regenerate the Python and Go bindings:

```bash
./generate_protos.sh
```

### Running Tests

#### Python (Admin & Simulator)
```bash
# Admin tests
cd sensor-admin && python3 -m unittest discover tests
# Simulator tests
cd service-1-python && python3 -m unittest test_main.py
```

#### Go (Processor)
```bash
cd service-2-go && go test ./...
```

### Troubleshooting

-   **View Logs**:
    ```bash
    podman-compose logs -f service-2-go      # Go subscriber logs
    podman-compose logs -f service-1-python  # Python simulator logs
    ```
-   **Restart a specific service**:
    ```bash
    podman-compose restart service-1-python
    ```
