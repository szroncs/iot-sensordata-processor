package storage

import (
	"log/slog"
	"os"
	
	"iot-sensordata-processor/service-2-go/gen/iot_pb"
)

// Storage defines the interface for data persistence
type Storage interface {
	Save(reading *iot_pb.SensorReading, valid bool, validationErr error) error
}

// JSONLoggerStorage persists telemetry to stdout using structured JSON logging
// which can easily be scraped by Promtail/Loki for Grafana visualization.
type JSONLoggerStorage struct {
	logger *slog.Logger
}

func NewJSONLoggerStorage() *JSONLoggerStorage {
	// Emit logs in JSON format for Grafana tracing
	handler := slog.NewJSONHandler(os.Stdout, nil)
	return &JSONLoggerStorage{
		logger: slog.New(handler),
	}
}

func (s *JSONLoggerStorage) Save(reading *iot_pb.SensorReading, valid bool, validationErr error) error {
	// Extract device and location
	deviceID := reading.GetDeviceId()
	location := reading.GetLocation()
	
	// Create baseline log attributes
	attrs := []any{
		slog.String("device_id", deviceID),
		slog.String("location", location),
		slog.Bool("valid", valid),
	}

	if !valid && validationErr != nil {
		attrs = append(attrs, slog.String("error", validationErr.Error()))
		s.logger.Warn("Faulty Telemetry Detected", attrs...)
		return nil
	}

	// Payload is valid, just log it normally for now.
	// In the future this is replaced by pushing to InfluxDB.
	s.logger.Info("Telemetry Persisted", attrs...)
	return nil
}
