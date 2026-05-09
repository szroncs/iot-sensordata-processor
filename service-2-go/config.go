package main

import "os"

// Config holds all runtime configuration sourced from environment variables.
// Every field maps to exactly one variable; defaults are applied by LoadConfig.
type Config struct {
	MQTTBroker          string // MQTT_BROKER           default: "localhost"
	MQTTPort            string // MQTT_PORT              default: "1883"
	MQTTTopic           string // MQTT_TOPIC             default: "telemetry/sensors"
	InfluxURL           string // INFLUX_URL             default: "http://localhost:8086"
	InfluxToken         string // INFLUX_TOKEN           (no default — must be set)
	InfluxOrg           string // INFLUX_ORG             default: "thesis_org"
	InfluxRawBucket     string // INFLUX_BUCKET_RAW      default: "raw_data"
	InfluxInvalidBucket string // INFLUX_BUCKET_INVALID  default: "invalid_data"
}

// LoadConfig reads environment variables and returns a fully populated Config.
// Fields with no env value fall back to their documented defaults.
func LoadConfig() Config {
	return Config{
		MQTTBroker:          getEnv("MQTT_BROKER", "localhost"),
		MQTTPort:            getEnv("MQTT_PORT", "1883"),
		MQTTTopic:           getEnv("MQTT_TOPIC", "telemetry/sensors"),
		InfluxURL:           getEnv("INFLUX_URL", "http://localhost:8086"),
		InfluxToken:         os.Getenv("INFLUX_TOKEN"), // no fallback
		InfluxOrg:           getEnv("INFLUX_ORG", "thesis_org"),
		InfluxRawBucket:     getEnv("INFLUX_BUCKET_RAW", "raw_data"),
		InfluxInvalidBucket: getEnv("INFLUX_BUCKET_INVALID", "invalid_data"),
	}
}

// getEnv returns the value of the named environment variable,
// or fallback when the variable is unset or empty.
func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
