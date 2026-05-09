import json
import logging
import os
import random
import sys
import time

import paho.mqtt.client as mqtt

# Add the 'gen/iot_pb' directory to the Python path to import the generated protobuf classes
sys.path.append(os.path.join(os.path.dirname(__file__), "gen", "iot_pb"))
import sensor_pb2
from google.protobuf.timestamp_pb2 import Timestamp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ── Environment configuration ─────────────────────────────────────────────────
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "telemetry/sensors")
DEBUG_CONSOLE_ONLY = os.getenv("DEBUG_CONSOLE_ONLY", "false").lower() == "true"
SENSOR_CONFIG_PATH = os.getenv("SENSOR_CONFIG_PATH", "./config/sensors.json")

# ── Physical sensor thresholds (hardware limits) ──────────────────────────────
# These constrain the simulated values to what the physical hardware can output.
# They are NOT the operational validation bounds used by service-2-go.
SENSOR_THRESHOLDS = {
    "temperature": {"min": -200.0, "max": 850.0},
    "humidity": {"min": 0.0, "max": 100.0},
    "gas": {
        "co2": {"min": 0.0, "max": 50000.0},
        "lpg": {"min": 0.0, "max": 10000.0},
    },
}

# ── Config loading ────────────────────────────────────────────────────────────


def load_sensor_config(path: str) -> list:
    """
    Load and return the sensors list from sensors.json.
    Exits the process on missing file or malformed JSON so the container
    restarts with a clear error rather than silently doing nothing.
    """
    try:
        with open(path, "r") as f:
            data = json.load(f)
        sensors = data.get("sensors", [])
        logging.info(f"Loaded {len(sensors)} sensor(s) from {path}")
        return sensors
    except FileNotFoundError:
        logging.error(f"Sensor config file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in sensor config file ({path}): {e}")
        sys.exit(1)


# ── Simulation functions ──────────────────────────────────────────────────────


def get_current_timestamp():
    ts = Timestamp()
    ts.GetCurrentTime()
    return ts


def simulate_temperature() -> sensor_pb2.TemperatureReading:
    t = SENSOR_THRESHOLDS["temperature"]
    val = random.gauss(20.0, 5.0)
    reading = sensor_pb2.TemperatureReading()
    reading.value = round(max(t["min"], min(t["max"], val)), 2)
    return reading


def simulate_humidity() -> sensor_pb2.HumidityReading:
    t = SENSOR_THRESHOLDS["humidity"]
    val = random.gauss(50.0, 10.0)
    reading = sensor_pb2.HumidityReading()
    reading.value = round(max(t["min"], min(t["max"], val)), 2)
    return reading


def simulate_gas() -> sensor_pb2.GasReading:
    t = SENSOR_THRESHOLDS["gas"]
    co2 = random.gauss(1000.0, 400.0)
    lpg = random.gauss(600.0, 300.0)
    reading = sensor_pb2.GasReading()
    reading.co2_ppm = round(max(t["co2"]["min"], min(t["co2"]["max"], co2)), 2)
    reading.lpg_presence = round(max(t["lpg"]["min"], min(t["lpg"]["max"], lpg)), 2)
    return reading


def simulate_door(is_open: bool) -> sensor_pb2.DoorReading:
    reading = sensor_pb2.DoorReading()
    reading.is_open = is_open
    return reading


def simulate_alert(is_active: bool, severity) -> sensor_pb2.AlertReading:
    reading = sensor_pb2.AlertReading()
    reading.active = is_active
    reading.severity = severity
    return reading


# ── Publishing ────────────────────────────────────────────────────────────────


def publish_reading(
    client, payload_type: str, device_id: str, location: str, reading_data, qos: int = 1
) -> None:
    reading = sensor_pb2.SensorReading()
    reading.device_id = device_id
    reading.location = location
    reading.ts.CopyFrom(get_current_timestamp())

    if payload_type == "temperature":
        reading.temperature.CopyFrom(reading_data)
        qos = 0
    elif payload_type == "humidity":
        reading.humidity.CopyFrom(reading_data)
    elif payload_type == "gas":
        reading.gas.CopyFrom(reading_data)
    elif payload_type == "door":
        reading.door.CopyFrom(reading_data)
    elif payload_type == "alert":
        reading.alert.CopyFrom(reading_data)
        qos = 2

    payload_bytes = reading.SerializeToString()

    if not DEBUG_CONSOLE_ONLY:
        client.publish(MQTT_TOPIC, payload_bytes, qos=qos)
        logging.info(
            f"Published {payload_type} reading for {device_id} "
            f"to {MQTT_TOPIC} ({len(payload_bytes)} bytes, QoS {qos})"
        )
    else:
        logging.info(f"[CONSOLE LOG] {payload_type} reading for {device_id}: {reading}")


# ── Per-sensor simulation state ───────────────────────────────────────────────


class SensorState:
    """
    Tracks all runtime mutable state for one sensor.
    Each sensor loaded from sensors.json gets its own SensorState instance.
    """

    def __init__(self, sensor_config: dict):
        self.config = sensor_config
        self.last_publish = 0.0

        # Type-specific extra state
        sensor_type = sensor_config["type"]
        if sensor_type == "door":
            self.door_is_open = False
        elif sensor_type == "alert":
            self.alert_is_active = False
            self.alert_severity = sensor_pb2.AlertReading.SEVERITY_INFO
            self.alert_start_time = 0.0


def tick_sensor(state: SensorState, now: float, client) -> None:
    """
    Process one 0.1-second simulation tick for a single sensor.
    Publishes a reading when the sensor's interval has elapsed,
    or immediately on a door state change.
    """
    cfg = state.config
    sensor_type = cfg["type"]
    device_id = cfg["id"]
    location = cfg["location"]

    if sensor_type == "temperature":
        freq = cfg.get("sample_frequency_seconds", 10)
        if now - state.last_publish >= freq:
            publish_reading(
                client, "temperature", device_id, location, simulate_temperature()
            )
            state.last_publish = now

    elif sensor_type == "humidity":
        freq = cfg.get("sample_frequency_seconds", 15)
        if now - state.last_publish >= freq:
            publish_reading(
                client, "humidity", device_id, location, simulate_humidity()
            )
            state.last_publish = now

    elif sensor_type == "gas":
        freq = cfg.get("sample_frequency_seconds", 3)
        if now - state.last_publish >= freq:
            publish_reading(client, "gas", device_id, location, simulate_gas())
            state.last_publish = now

    elif sensor_type == "door":
        # ~1% chance per 0.1s tick → average ~10s between state changes
        door_changed = False
        if random.random() < 0.01:
            state.door_is_open = not state.door_is_open
            door_changed = True
        # Publish on state change OR as a 30-second keepalive
        if door_changed or (now - state.last_publish >= 30):
            publish_reading(
                client, "door", device_id, location, simulate_door(state.door_is_open)
            )
            state.last_publish = now

    elif sensor_type == "alert":
        # Transition: idle → active
        if not state.alert_is_active:
            if random.random() < 0.005:
                state.alert_is_active = True
                state.alert_severity = random.choice(
                    [
                        sensor_pb2.AlertReading.SEVERITY_INFO,
                        sensor_pb2.AlertReading.SEVERITY_WARNING,
                        sensor_pb2.AlertReading.SEVERITY_CRITICAL,
                    ]
                )
                state.alert_start_time = now
        else:
            # Transition: active → resolved (earliest after 5 s)
            if (now - state.alert_start_time) > 5 and random.random() < 0.05:
                state.alert_is_active = False

        # Publish interval: 1 s when alerting, 60 s when idle
        alert_interval = 1 if state.alert_is_active else 60
        if now - state.last_publish >= alert_interval:
            publish_reading(
                client,
                "alert",
                device_id,
                location,
                simulate_alert(state.alert_is_active, state.alert_severity),
            )
            state.last_publish = now


# ── MQTT callbacks ────────────────────────────────────────────────────────────


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        logging.error(f"Failed to connect to MQTT broker, return code: {rc}")


# ── Entry point ───────────────────────────────────────────────────────────────


def main():
    sensors = load_sensor_config(SENSOR_CONFIG_PATH)
    sensor_states = [SensorState(s) for s in sensors]
    logging.info(f"Initialized {len(sensor_states)} sensor simulation(s).")

    client = mqtt.Client(client_id="python-simulator-01")
    client.on_connect = on_connect

    if not DEBUG_CONSOLE_ONLY:
        logging.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            sys.exit(1)
        client.loop_start()
    else:
        logging.info("DEBUG_CONSOLE_ONLY mode — bypassing MQTT connection.")

    try:
        while True:
            now = time.time()
            for state in sensor_states:
                tick_sensor(state, now, client)
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Simulation stopped by user.")
    finally:
        if not DEBUG_CONSOLE_ONLY:
            client.loop_stop()
            client.disconnect()
            logging.info("Disconnected from MQTT broker.")


if __name__ == "__main__":
    main()
