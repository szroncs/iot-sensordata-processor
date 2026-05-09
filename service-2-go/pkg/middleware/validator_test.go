package middleware

import (
	"testing"

	"iot-sensordata-processor/service-2-go/gen/iot_pb"
)

func TestValidateTemperature(t *testing.T) {
	tests := []struct {
		name    string
		value   float32
		wantErr bool
	}{
		{"Valid low", 10.0, false},
		{"Valid high", 28.0, false},
		{"Valid mid", 20.0, false},
		{"Invalid too low", 9.9, true},
		{"Invalid too high", 28.1, true},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			reading := &iot_pb.SensorReading{
				Payload: &iot_pb.SensorReading_Temperature{
					Temperature: &iot_pb.TemperatureReading{Value: tc.value},
				},
			}
			err := Validate(reading)
			if (err != nil) != tc.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tc.wantErr)
			}
		})
	}
}

func TestValidateHumidity(t *testing.T) {
	tests := []struct {
		name    string
		value   float32
		wantErr bool
	}{
		{"Valid low", 35.0, false},
		{"Valid high", 65.0, false},
		{"Valid mid", 50.0, false},
		{"Invalid too low", 34.9, true},
		{"Invalid too high", 65.1, true},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			reading := &iot_pb.SensorReading{
				Payload: &iot_pb.SensorReading_Humidity{
					Humidity: &iot_pb.HumidityReading{Value: tc.value},
				},
			}
			err := Validate(reading)
			if (err != nil) != tc.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tc.wantErr)
			}
		})
	}
}

func TestValidateGas(t *testing.T) {
	tests := []struct {
		name    string
		co2     float32
		lpg     float32
		wantErr bool
	}{
		{"Valid", 1000.0, 500.0, false},
		{"Valid max", 1800.0, 1100.0, false},
		{"Invalid CO2 too high", 1800.1, 500.0, true},
		{"Invalid CO2 negative", -1.0, 500.0, true},
		{"Invalid LPG too high", 1000.0, 1100.1, true},
		{"Invalid LPG negative", 1000.0, -1.0, true},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			reading := &iot_pb.SensorReading{
				Payload: &iot_pb.SensorReading_Gas{
					Gas: &iot_pb.GasReading{
						Co2Ppm:      tc.co2,
						LpgPresence: tc.lpg,
					},
				},
			}
			err := Validate(reading)
			if (err != nil) != tc.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tc.wantErr)
			}
		})
	}
}

func TestValidateNilAndEmpty(t *testing.T) {
	t.Run("Nil reading", func(t *testing.T) {
		if err := Validate(nil); err == nil {
			t.Error("Validate() expected error for nil reading")
		}
	})

	t.Run("Missing payload", func(t *testing.T) {
		reading := &iot_pb.SensorReading{}
		if err := Validate(reading); err == nil {
			t.Error("Validate() expected error for missing payload")
		}
	})
}
