package middleware

import (
	"log/slog"

	"iot-sensordata-processor/service-2-go/gen/iot_pb"
	"iot-sensordata-processor/service-2-go/pkg/storage"

	"google.golang.org/protobuf/proto"
)

type Pipeline struct {
	store storage.Storage
}

func NewPipeline(store storage.Storage) *Pipeline {
	return &Pipeline{
		store: store,
	}
}

// ProcessMessage is the main function spawned for every MQTT telemetry event
func (p *Pipeline) ProcessMessage(payloadBytes []byte) {
	// Step 1: Decode
	reading := &iot_pb.SensorReading{}
	if err := proto.Unmarshal(payloadBytes, reading); err != nil {
		slog.Error("Failed to decode Protobuf payload", slog.String("error", err.Error()))
		return
	}

	// Step 2: Validate
	err := Validate(reading)

	// Step 3: Persist results (including errors so Grafana can visualize them)
	if err != nil {
		p.store.Save(reading, false, err)
	} else {
		p.store.Save(reading, true, nil)
	}
}
