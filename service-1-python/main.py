import os
import sys
import time
import random
import logging
from datetime import datetime

import paho.mqtt.client as mqtt

# Add the 'gen/iot_pb' directory to the Python path to import the generated protobuf classes
sys.path.append(os.path.join(os.path.dirname(__file__), 'gen', 'iot_pb'))
import sensor_pb2
from google.protobuf.timestamp_pb2 import Timestamp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'telemetry/sensors')
INTERVAL_SECONDS = float(os.getenv('INTERVAL_SECONDS', 2.0))
DEBUG_CONSOLE_ONLY = os.getenv('DEBUG_CONSOLE_ONLY', 'false').lower() == 'true'

def get_current_timestamp():
    ts = Timestamp()
    ts.GetCurrentTime()
    return ts

def simulate_temperature():
    reading = sensor_pb2.TemperatureReading()
    # Normal distribution centered around 20C with a stddev of 5C
    val = random.gauss(20.0, 5.0)
    # Clamp to physical RTD sensor limits (-200 to 850)
    reading.value = round(max(-200.0, min(850.0, val)), 2)
    return reading

def simulate_humidity():
    reading = sensor_pb2.HumidityReading()
    # Normal distribution centered around 50% with a stddev of 10%
    val = random.gauss(50.0, 10.0)
    # Clamp to physical 0-100% RH limits
    reading.value = round(max(0.0, min(100.0, val)), 2)
    return reading

def simulate_gas():
    reading = sensor_pb2.GasReading()
    # Normal distribution: CO2 (mean 1000, std 400), LPG (mean 600, std 300)
    co2 = random.gauss(1000.0, 400.0)
    lpg = random.gauss(600.0, 300.0)
    # Clamp to physical limits
    reading.co2_ppm = round(max(0.0, min(50000.0, co2)), 2)
    reading.lpg_presence = round(max(0.0, min(10000.0, lpg)), 2)
    return reading

def simulate_door(is_open):
    reading = sensor_pb2.DoorReading()
    reading.is_open = is_open
    return reading

def simulate_alert(is_active, severity):
    reading = sensor_pb2.AlertReading()
    reading.active = is_active
    if severity is not None:
        reading.severity = severity
    return reading

def publish_reading(client, payload_type, device_id, location, reading_data, qos=1):
    reading = sensor_pb2.SensorReading()
    reading.device_id = device_id
    reading.location = location
    reading.ts.CopyFrom(get_current_timestamp())
    
    if payload_type == 'temperature':
        reading.temperature.CopyFrom(reading_data)
        qos = 0
    elif payload_type == 'humidity':
        reading.humidity.CopyFrom(reading_data)
    elif payload_type == 'gas':
        reading.gas.CopyFrom(reading_data)
    elif payload_type == 'door':
        reading.door.CopyFrom(reading_data)
    elif payload_type == 'alert':
        reading.alert.CopyFrom(reading_data)
        qos = 2
        
    payload_bytes = reading.SerializeToString()
    
    if not DEBUG_CONSOLE_ONLY:
        client.publish(MQTT_TOPIC, payload_bytes, qos=qos)
        logging.info(f"Published {payload_type} reading for {device_id} to {MQTT_TOPIC} ({len(payload_bytes)} bytes, QoS {qos})")
    else:
        logging.info(f"[CONSOLE LOG] {payload_type} reading for {device_id}: {reading}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        logging.error(f"Failed to connect, return code {rc}")

class SimulationState:
    def __init__(self):
        self.door_is_open = False
        self.last_door_publish = 0
        
        self.alert_is_active = False
        self.alert_severity = sensor_pb2.AlertReading.SEVERITY_INFO
        self.last_alert_publish = 0
        self.alert_start_time = 0
        
        self.last_temp_publish = 0
        self.last_humidity_publish = 0
        self.last_gas_publish = 0

def main():
    client = mqtt.Client(client_id="python-simulator-01")
    client.on_connect = on_connect
    
    if not DEBUG_CONSOLE_ONLY:
        logging.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            logging.error(f"Error connecting to MQTT: {e}")
            logging.info("Continuing anyway (container might crash or retry if configured).")
            sys.exit(1)

        client.loop_start()
    else:
        logging.info("DEBUG_CONSOLE_ONLY is set. Bypassing MQTT connection.")

    state = SimulationState()
    
    try:
        while True:
            now = time.time()
            
            # Temperature: 10s
            if now - state.last_temp_publish >= 10:
                publish_reading(client, 'temperature', 'sim-temperature-01', 'Warehouse-B', simulate_temperature())
                state.last_temp_publish = now
                
            # Humidity: 15s
            if now - state.last_humidity_publish >= 15:
                publish_reading(client, 'humidity', 'sim-humidity-01', 'Warehouse-B', simulate_humidity())
                state.last_humidity_publish = now
                
            # Gas (CO2 & LPG): 3s
            if now - state.last_gas_publish >= 3:
                publish_reading(client, 'gas', 'sim-gas-01', 'Office-C', simulate_gas())
                state.last_gas_publish = now
                
            # Door: send on state change OR every 30s
            door_changed = False
            # 1% chance to change state every 0.1s tick -> avg 10s between changes
            if random.random() < 0.01:
                state.door_is_open = not state.door_is_open
                door_changed = True
                
            if door_changed or (now - state.last_door_publish >= 30):
                publish_reading(client, 'door', 'sim-door-01', 'Factory-Floor-A', simulate_door(state.door_is_open))
                state.last_door_publish = now
                
            # Alert: 1s if alerting, 60s if not alerting
            if not state.alert_is_active:
                # Small chance to trigger an alert
                if random.random() < 0.005: 
                    state.alert_is_active = True
                    state.alert_severity = random.choice([
                        sensor_pb2.AlertReading.SEVERITY_INFO,
                        sensor_pb2.AlertReading.SEVERITY_WARNING,
                        sensor_pb2.AlertReading.SEVERITY_CRITICAL
                    ])
                    state.alert_start_time = now
            else:
                # If active for at least 5s, chance to resolve
                if (now - state.alert_start_time) > 5 and random.random() < 0.05:
                    state.alert_is_active = False
            
            alert_interval = 1 if state.alert_is_active else 60
            if now - state.last_alert_publish >= alert_interval:
                publish_reading(client, 'alert', 'sim-alert-01', 'Factory-Floor-A', simulate_alert(state.alert_is_active, state.alert_severity))
                state.last_alert_publish = now
                
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
