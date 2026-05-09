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

def simulate_door():
    reading = sensor_pb2.DoorReading()
    reading.is_open = random.choice([True, False, False, False]) # Usually closed
    return reading

def simulate_alert():
    reading = sensor_pb2.AlertReading()
    reading.active = True
    reading.severity = random.choice([
        sensor_pb2.AlertReading.SEVERITY_INFO,
        sensor_pb2.AlertReading.SEVERITY_WARNING,
        sensor_pb2.AlertReading.SEVERITY_CRITICAL
    ])
    return reading

def create_sensor_reading():
    reading = sensor_pb2.SensorReading()
    
    # Base fields
    sensor_types = ['temperature', 'humidity', 'gas', 'door', 'alert']
    chosen_type = random.choice(sensor_types)
    
    reading.device_id = f"sim-{chosen_type}-01"
    reading.location = random.choice(["Factory-Floor-A", "Warehouse-B", "Office-C"])
    reading.ts.CopyFrom(get_current_timestamp())

    # Set the oneof payload
    if chosen_type == 'temperature':
        reading.temperature.CopyFrom(simulate_temperature())
    elif chosen_type == 'humidity':
        reading.humidity.CopyFrom(simulate_humidity())
    elif chosen_type == 'gas':
        reading.gas.CopyFrom(simulate_gas())
    elif chosen_type == 'door':
        reading.door.CopyFrom(simulate_door())
    elif chosen_type == 'alert':
        reading.alert.CopyFrom(simulate_alert())

    return reading

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        logging.error(f"Failed to connect, return code {rc}")

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
            # Let it fail if not available, useful for docker restart policies
            sys.exit(1)

        client.loop_start()
    else:
        logging.info("DEBUG_CONSOLE_ONLY is set. Bypassing MQTT connection.")

    try:
        while True:
            # Generate a random payload
            reading = create_sensor_reading()
            
            # Serialize
            payload_bytes = reading.SerializeToString()
            
            payload_type = reading.WhichOneof("payload")
            
            # Determine QoS based on thesis rules
            qos = 1
            if payload_type == "temperature":
                qos = 0
            elif payload_type == "alert":
                qos = 2
            
            if not DEBUG_CONSOLE_ONLY:
                # Publish
                client.publish(MQTT_TOPIC, payload_bytes, qos=qos)
                logging.info(f"Published {payload_type} reading for {reading.device_id} to {MQTT_TOPIC} ({len(payload_bytes)} bytes, QoS {qos})")
            else:
                logging.info(f"[CONSOLE LOG] {payload_type} reading for {reading.device_id}: {reading}")
            
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Simulation stopped by user.")
    finally:
        if not DEBUG_CONSOLE_ONLY:
            client.loop_stop()
            client.disconnect()
            logging.info("Disconnected from MQTT broker.")

if __name__ == "__main__":
    main()
