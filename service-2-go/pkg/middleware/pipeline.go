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

// ProcessMessage handles one MQTT payload (decode, validate, save)
func (p *Pipeline) ProcessMessage(payloadBytes []byte) {
	slog.Info("Received message from MQTT", slog.Int("size", len(payloadBytes)))

	reading := &iot_pb.SensorReading{}
	if err := proto.Unmarshal(payloadBytes, reading); err != nil {
		slog.Error("Failed to decode Protobuf payload", slog.String("error", err.Error()))
		return
	}

	err := Validate(reading)

	if err != nil {
		p.store.Save(reading, false, err)
	} else {
		p.store.Save(reading, true, nil)
	}
}
