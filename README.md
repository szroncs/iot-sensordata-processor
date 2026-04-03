# IoT telemetry optimization: binary serialization and middleware-based sensor data validation

Draft project structure

iot-data-pipeline/
├── proto/
│   └── sensor.proto           # The "Contract"
├── service-1-python/
│   ├── gen/                   # Generated Protobuf code (Python)
│   ├── main.py                # Mock data logic
│   ├── requirements.txt
│   └── Dockerfile
├── service-2-go/
│   ├── gen/                   # Generated Protobuf code (Go)
│   ├── pkg/
│   │   ├── middleware/        # Logic for log/validate/persist
│   │   └── influx/            # InfluxDB client wrapper
│   ├── main.go                # MQTT Subscriber & Pipeline setup
│   ├── go.mod
│   └── Dockerfile
├── infrastructure/
│   ├── mosquitto.conf         # MQTT broker config
│   └── grafana/               # Pre-configured dashboard JSONs
├── scripts/
│   └── generate_protos.sh     # Script to run protoc for both langs
├── podman-compose.yaml        # Main orchestration file
└── README.md

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
Data serialization and data structure definition.


### MQTT - mosquitto
Currently, there is no `mosquitto.conf` implemented. An external or default Mosquitto instance needs to be used for the current state of the application.

### InfluxDB
Currently not fully implemented. As of now, `service-2-go` relies on `pkg/storage/logger.go` instead of a fully implemented `pkg/influx` driver.

### Grafana
Dashboards are currently pending implementation.

### Podman
The `podman-compose.yaml` file is pending creation. You will need to build and run the provided `Dockerfile`s manually for now.


## Current State vs Draft Structure
There are some discrepancies between the planned Draft structure and the actual implementation:
- `generate_protos.sh` is located in the root directory rather than in the `scripts/` directory.
- The `infrastructure/` directory is currently created as `infrastruture/` and is empty.
- `service-2-go/pkg/influx/` is not yet present; there is a `pkg/storage/logger.go` instead which currently logs data to the console.
- The project is still missing full InfluxDB and Grafana integration.
- To generate protobufs: run `./generate_protos.sh` from the root.
- To run Python mock data: `cd service-1-python && source venv/bin/activate && python main.py`
- To run Go backend: `cd service-2-go && go run main.go`



ToDo:

1. Bring up the network using the compose file we generated earlier:
```sh
podman-compose up --build -d
```
2. You can then attach to the Go subscriber logs and watch the messages come in and be processed by the middleware:
```sh
podman-compose logs -f service-2-go
```
3. To watch the Python backend serialize the data into Protocol Buffers and publish them with the assigned QoS flags, tail its logs:
```sh
podman-compose logs -f service-1-python
```

If you ever want to test the Python payload generation logic *without* an MQTT broker running, you can also run the Python service using its built-in bypass flag:
```sh
cd service-1-python
source venv/bin/activate
DEBUG_CONSOLE_ONLY=true python main.py
```

Let me know if you want to proceed with storing the data into InfluxDB next (which is still a mock method in `pkg/storage/logger.go`)!