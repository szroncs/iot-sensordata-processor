package storage

import "iot-sensordata-processor/service-2-go/gen/iot_pb"

// Storage interface is the "contract" for data persistance.
// reading - pointer to prootobuf reading; valid - true/false; validationErr - builtin error interface
type Storage interface {
	Save(reading *iot_pb.SensorReading, valid bool, validationErr error) error
}
