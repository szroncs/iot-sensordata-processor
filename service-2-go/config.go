package main

import "os"

// Go doesn't have built-in syntax for default values that's why I've documented here
// although default values are set in LoadConfig function as fallback values
type Config struct {
	MQTTBroker          string // MQTT_BROKER           default: "localhost"
	MQTTPort            string // MQTT_PORT              default: "1883"
	MQTTTopic           string // MQTT_TOPIC             default: "telemetry/sensors"
	InfluxURL           string // INFLUX_URL             default: "http://localhost:8086"
	InfluxToken         string // INFLUX_TOKEN           (no default — must be set)
	InfluxOrg           string // INFLUX_ORG             default: "T4PIJ6_org"
	InfluxRawBucket     string // INFLUX_BUCKET_RAW      default: "raw_data"
	InfluxInvalidBucket string // INFLUX_BUCKET_INVALID  default: "invalid_data"
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
// ! if InfluxToken is empty the main.go/cfg.InfluxToken will be empty --> influx.go/NewInfluxStorage will try to connect without authentication
// as professional as I am, in the podman-compose.yaml I set the token: INFLUX_TOKEN=my-super-secret-auth-token
func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
