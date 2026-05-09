package storage

import (
	"context"
	"log/slog"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"iot-sensordata-processor/service-2-go/gen/iot_pb"
)

type InfluxStorage struct {
	client          influxdb2.Client
	writeAPIRaw     api.WriteAPIBlocking
	writeAPIInvalid api.WriteAPIBlocking
}

func NewInfluxStorage(url, token, org, rawBucket, invalidBucket string) *InfluxStorage {
	client := influxdb2.NewClient(url, token)

	writeAPIRaw := client.WriteAPIBlocking(org, rawBucket)
	writeAPIInvalid := client.WriteAPIBlocking(org, invalidBucket)

	return &InfluxStorage{
		client:          client,
		writeAPIRaw:     writeAPIRaw,
		writeAPIInvalid: writeAPIInvalid,
	}
}

func (s *InfluxStorage) Save(reading *iot_pb.SensorReading, valid bool, validationErr error) error {
	deviceID := reading.GetDeviceId()
	location := reading.GetLocation()
	
	// Convert Google Protobuf Timestamp to Go Time
	timestamp := reading.GetTs().AsTime()

	tags := map[string]string{
		"device_id": deviceID,
		"location":  location,
	}

	fields := map[string]interface{}{}
	payloadType := "unknown"

	if reading.GetPayload() != nil {
		switch v := reading.GetPayload().(type) {
		case *iot_pb.SensorReading_Temperature:
			fields["temperature"] = v.Temperature.GetValue()
			payloadType = "temperature"
		case *iot_pb.SensorReading_Humidity:
			fields["humidity"] = v.Humidity.GetValue()
			payloadType = "humidity"
		case *iot_pb.SensorReading_Gas:
			fields["co2"] = v.Gas.GetCo2Ppm()
			fields["lpg"] = v.Gas.GetLpgPresence()
			payloadType = "gas"
		case *iot_pb.SensorReading_Door:
			fields["is_open"] = v.Door.GetIsOpen()
			payloadType = "door"
		case *iot_pb.SensorReading_Alert:
			fields["active"] = v.Alert.GetActive()
			fields["severity"] = v.Alert.GetSeverity().String()
			payloadType = "alert"
		}
	}

	tags["payload_type"] = payloadType

	if !valid && validationErr != nil {
		fields["error"] = validationErr.Error()
	}

	p := influxdb2.NewPoint("sensor_telemetry",
		tags,
		fields,
		timestamp)

	// Always write raw telemetry
	err := s.writeAPIRaw.WritePoint(context.Background(), p)
	if err != nil {
		slog.Error("Failed to write to raw InfluxDB bucket", slog.String("error", err.Error()))
		return err
	}

	// Additionally write to invalid bucket if invalid
	if !valid {
		err = s.writeAPIInvalid.WritePoint(context.Background(), p)
		if err != nil {
			slog.Error("Failed to write to invalid InfluxDB bucket", slog.String("error", err.Error()))
			return err
		}
	}

	return nil
}

func (s *InfluxStorage) Close() {
	s.client.Close()
}
