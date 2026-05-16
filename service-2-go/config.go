package main

import "os"

// Go doesn't have built-in syntax for default values that's why
// values are set in LoadConfig function as fallback values
type Config struct {
	MQTTBroker          string
	MQTTPort            string
	MQTTTopic           string
	InfluxURL           string
	InfluxToken         string
	InfluxOrg           string
	InfluxRawBucket     string
	InfluxInvalidBucket string
}

// LoadConfig reads environment variables and returns a fully populated Config.
func LoadConfig() Config {
	return Config{
		MQTTBroker:          getEnv("MQTT_BROKER", "localhost"),
		MQTTPort:            getEnv("MQTT_PORT", "1883"),
		MQTTTopic:           getEnv("MQTT_TOPIC", "telemetry/sensors"),
		InfluxURL:           getEnv("INFLUX_URL", "http://localhost:8086"),
		InfluxToken:         os.Getenv("INFLUX_TOKEN"), // no fallback
		InfluxOrg:           getEnv("INFLUX_ORG", "T4PIJ6_org"),
		InfluxRawBucket:     getEnv("INFLUX_BUCKET_RAW", "raw_data"),
		InfluxInvalidBucket: getEnv("INFLUX_BUCKET_INVALID", "invalid_data"),
	}
}

// getEnv returns the value of the named environment variable,
// or fallback when the variable is unset or empty.
//
// ! if InfluxToken is empty the main.go/cfg.InfluxToken will be empty --> influx.go/NewInfluxStorage
// will try to connect without authentication
// as professional as I am, in the podman-compose.yaml I set the token: INFLUX_TOKEN=my-super-secret-auth-token
func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
