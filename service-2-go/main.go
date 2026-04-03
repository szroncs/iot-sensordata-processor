package main

import (
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"iot-sensordata-processor/service-2-go/pkg/middleware"
	"iot-sensordata-processor/service-2-go/pkg/storage"
)

func main() {
	// 1. Environment configuration
	broker := os.Getenv("MQTT_BROKER")
	if broker == "" {
		broker = "localhost"
	}
	portStr := os.Getenv("MQTT_PORT")
	if portStr == "" {
		portStr = "1883"
	}
	topic := os.Getenv("MQTT_TOPIC")
	if topic == "" {
		topic = "telemetry/sensors"
	}

	brokerURL := "tcp://" + broker + ":" + portStr

	// 2. Initialize Pipeline & Storage
	slog.Info("Initializing storage mechanism")
	jsonStore := storage.NewJSONLoggerStorage()

	slog.Info("Building middleware pipeline")
	pipeline := middleware.NewPipeline(jsonStore)

	// 3. Configure MQTT Client
	opts := mqtt.NewClientOptions()
	opts.AddBroker(brokerURL)
	opts.SetClientID("go-processor-01")
	opts.SetCleanSession(true)
	
	// Define the message handler logic
	opts.SetDefaultPublishHandler(func(client mqtt.Client, msg mqtt.Message) {
		// Offload processing to a dedicated Goroutine (Fan-Out parallelism)
		// ensuring the MQTT loop is never blocked!
		go pipeline.ProcessMessage(msg.Payload())
	})

	opts.OnConnect = func(client mqtt.Client) {
		slog.Info("Connected to MQTT broker", slog.String("url", brokerURL))
		// Subscribe upon connecting with QoS 2 to ensure we don't downgrade alerts
		if token := client.Subscribe(topic, 2, nil); token.Wait() && token.Error() != nil {
			slog.Error("Failed to subscribe to MQTT topic", slog.String("error", token.Error().Error()))
			os.Exit(1)
		}
		slog.Info("Subscribed successfully", slog.String("topic", topic))
	}

	opts.OnConnectionLost = func(client mqtt.Client, err error) {
		slog.Warn("Lost connection to MQTT broker", slog.String("error", err.Error()))
	}

	// 4. Start Client
	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		slog.Error("Failed to connect to MQTT broker initially", slog.String("error", token.Error().Error()))
		// Depending on docker restart policy, letting it crash so the orchestrator reboots it is idiomatic
		os.Exit(1)
	}

	// 5. Wait for termination signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	<-sigChan

	slog.Info("Shutting down service-2-go...")
	client.Disconnect(250)
	slog.Info("Shutdown complete")
}
