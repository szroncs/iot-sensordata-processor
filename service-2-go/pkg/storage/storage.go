package storage

import "iot-sensordata-processor/service-2-go/gen/iot_pb"

// Storage is the persistence contract for sensor telemetry.
// Any backend (InfluxDB, in-memory, file, etc.) must satisfy this interface.
// The valid flag signals whether the reading passed middleware validation;
// validationErr carries the reason when valid is false.
type Storage interface {
	Save(reading *iot_pb.SensorReading, valid bool, validationErr error) error
}
