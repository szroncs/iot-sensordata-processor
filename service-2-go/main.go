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

	// 1. Initialize Storage & Pipeline
	slog.Info("Initializing InfluxDB storage", slog.String("url", cfg.InfluxURL))
	influxStore := storage.NewInfluxStorage(
		cfg.InfluxURL,
		cfg.InfluxToken,
		cfg.InfluxOrg,
		cfg.InfluxRawBucket,
		cfg.InfluxInvalidBucket,
	)
	defer influxStore.Close()

	slog.Info("Building middleware pipeline")
	pipeline := middleware.NewPipeline(influxStore)

	// 2. Configure MQTT Client
	opts := mqtt.NewClientOptions()
	opts.AddBroker(brokerURL)
	opts.SetClientID("go-processor-01")
	opts.SetCleanSession(true)

	opts.SetDefaultPublishHandler(func(client mqtt.Client, msg mqtt.Message) {
		// Offload processing to a dedicated Goroutine (Fan-Out parallelism)
		// ensuring the MQTT loop is never blocked!
		go pipeline.ProcessMessage(msg.Payload())
	})

	opts.OnConnect = func(client mqtt.Client) {
		slog.Info("Connected to MQTT broker", slog.String("url", brokerURL))
		// Subscribe upon connecting with QoS 2 to ensure we don't downgrade alerts
		if token := client.Subscribe(cfg.MQTTTopic, 2, nil); token.Wait() && token.Error() != nil {
			slog.Error("Failed to subscribe to MQTT topic", slog.String("error", token.Error().Error()))
			os.Exit(1)
		}
		slog.Info("Subscribed successfully", slog.String("topic", cfg.MQTTTopic))
	}

	opts.OnConnectionLost = func(client mqtt.Client, err error) {
		slog.Warn("Lost connection to MQTT broker", slog.String("error", err.Error()))
	}

	// 3. Start Client
	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		slog.Error("Failed to connect to MQTT broker initially", slog.String("error", token.Error().Error()))
		// Letting it crash is idiomatic — the container orchestrator will restart it
		os.Exit(1)
	}

	// 4. Wait for termination signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	<-sigChan

	slog.Info("Shutting down service-2-go...")
	client.Disconnect(250)
	slog.Info("Shutdown complete")
}
