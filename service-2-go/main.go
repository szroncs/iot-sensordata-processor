package main

import (
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"iot-sensordata-processor/service-2-go/pkg/middleware"
	"iot-sensordata-processor/service-2-go/pkg/storage"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

func main() {
	cfg := LoadConfig()
	brokerURL := "tcp://" + cfg.MQTTBroker + ":" + cfg.MQTTPort

	// Initialize Storage & Pipeline
	slog.Info("Initializing InfluxDB storage", slog.String("url", cfg.InfluxURL))
	influxStore := storage.NewInfluxStorage(
		cfg.InfluxURL,
		cfg.InfluxToken,
		cfg.InfluxOrg,
		cfg.InfluxRawBucket,
		cfg.InfluxInvalidBucket,
	)
	defer influxStore.Close()

	slog.Info("Initializing middleware pipeline")
	pipeline := middleware.NewPipeline(influxStore)

	// Configure MQTT Client --> https://pkg.go.dev/github.com/eclipse/paho.mqtt.golang#NewClientOptions
	opts := mqtt.NewClientOptions()
	opts.AddBroker(brokerURL)
	opts.SetClientID("go-processor-01")
	opts.SetCleanSession(true)

	opts.SetDefaultPublishHandler(func(client mqtt.Client, msg mqtt.Message) {
		// Handle each message in its own goroutine so the MQTT loop is never blocked
		// --> https://pkg.go.dev/github.com/eclipse/paho.mqtt.golang#ClientOptions.SetDefaultPublishHandler
		go pipeline.ProcessMessage(msg.Payload())
	})

	opts.OnConnect = func(client mqtt.Client) {
		slog.Info("Connected to MQTT broker", slog.String("url", brokerURL))
		// QoS 2 on subscribe (Exactly once delivery)
		if token := client.Subscribe(cfg.MQTTTopic, 2, nil); token.Wait() && token.Error() != nil {
			slog.Error("Failed to subscribe to MQTT topic", slog.String("error", token.Error().Error()))
			os.Exit(1)
		}
		slog.Info("Subscribed successfully", slog.String("topic", cfg.MQTTTopic))
	}

	opts.OnConnectionLost = func(client mqtt.Client, err error) {
		slog.Warn("Lost connection to MQTT broker", slog.String("error", err.Error()))
	}

	// https://pkg.go.dev/github.com/eclipse/paho.mqtt.golang#NewClient
	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		slog.Error("Failed to connect to MQTT broker initially", slog.String("error", token.Error().Error()))
		// crash and let Podman restart
		os.Exit(1)
	}

	// Listen to signal from buffered channel
	// os.Interrupt -> POSIX SIGINT user interruption
	// syscall.SIGTERM -> gracefull shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	<-sigChan

	slog.Info("Shutting down service-2-go...")
	client.Disconnect(250)
	slog.Info("Shutdown complete")
}
