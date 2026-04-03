package middleware

import (
	"errors"
	"fmt"

	"iot-sensordata-processor/service-2-go/gen/iot_pb"
)

// Validate checks the sensor reading against predefined physical & industrial limits.
func Validate(reading *iot_pb.SensorReading) error {
	if reading == nil {
		return errors.New("nil sensor reading")
	}

	payload := reading.GetPayload()
	if payload == nil {
		return errors.New("missing sensor payload")
	}

	switch v := payload.(type) {
	case *iot_pb.SensorReading_Temperature:
		temp := v.Temperature.GetValue()
		if temp < -200.0 || temp > 850.0 {
			return fmt.Errorf("temperature out of bounds: %.2f°C", temp)
		}
	case *iot_pb.SensorReading_Humidity:
		hum := v.Humidity.GetValue()
		if hum < 0.0 || hum > 100.0 {
			return fmt.Errorf("humidity out of bounds: %.2f%%", hum)
		}
	case *iot_pb.SensorReading_Gas:
		co2 := v.Gas.GetCo2Ppm()
		lpg := v.Gas.GetLpgPresence()
		if co2 < 0.0 || co2 > 50000.0 {
			return fmt.Errorf("CO2 out of bounds: %.2f ppm", co2)
		}
		if lpg < 0.0 {
			// Usually can't be negative
			return fmt.Errorf("LPG out of bounds: %.2f ppm", lpg)
		}
	case *iot_pb.SensorReading_Door:
		// Booleans are always valid
	case *iot_pb.SensorReading_Alert:
		// Alerts are logic-driven, usually valid
	default:
		return fmt.Errorf("unknown payload type")
	}

	return nil
}
