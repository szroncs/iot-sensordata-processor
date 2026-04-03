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
`paho-mqtt` -- https://pypi.org/project/paho-mqtt/

### Go


### ProtoBuf
```sh
sudo dnf inslatt protobuf-compiler
```

#### Go protoc plugin
```sh
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
```

### MQTT - mosquitto



### InfluxDB

































































































































#### Go influx driver
```sh
go get github.com/influxdata/influxdb-client-go/v2
```


### Grafana


### Podman
