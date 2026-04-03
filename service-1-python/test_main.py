import sys
import os
import unittest

# Append gen/iot_pb to python path so we can import sensor_pb2
sys.path.append(os.path.join(os.path.dirname(__file__), 'gen', 'iot_pb'))

import sensor_pb2
from main import simulate_temperature, simulate_humidity, simulate_gas, simulate_alert, create_sensor_reading

class TestSensorSimulator(unittest.TestCase):

    def test_simulate_temperature(self):
        reading = simulate_temperature()
        self.assertIsInstance(reading, sensor_pb2.TemperatureReading)
        self.assertGreaterEqual(reading.value, -200.0)
        self.assertLessEqual(reading.value, 850.0)

    def test_simulate_humidity(self):
        reading = simulate_humidity()
        self.assertIsInstance(reading, sensor_pb2.HumidityReading)
        self.assertGreaterEqual(reading.value, 0.0)
        self.assertLessEqual(reading.value, 100.0)

    def test_simulate_gas(self):
        reading = simulate_gas()
        self.assertIsInstance(reading, sensor_pb2.GasReading)
        self.assertGreaterEqual(reading.co2_ppm, 0.0)
        self.assertLessEqual(reading.co2_ppm, 50000.0)
        self.assertGreaterEqual(reading.lpg_presence, 200.0)
        self.assertLessEqual(reading.lpg_presence, 10000.0)

    def test_simulate_alert(self):
        reading = simulate_alert()
        self.assertIsInstance(reading, sensor_pb2.AlertReading)
        self.assertTrue(reading.active)
        self.assertIn(reading.severity, [
            sensor_pb2.AlertReading.SEVERITY_INFO,
            sensor_pb2.AlertReading.SEVERITY_WARNING,
            sensor_pb2.AlertReading.SEVERITY_CRITICAL
        ])

    def test_create_sensor_reading(self):
        # Run multiple times to ensure we hit different cases due to randomness
        for _ in range(20):
            reading = create_sensor_reading()
            payload_type = reading.WhichOneof("payload")
            self.assertIsNotNone(payload_type)
            self.assertTrue(reading.device_id.startswith(f"sim-{payload_type}"))
            self.assertIn(reading.location, ["Factory-Floor-A", "Warehouse-B", "Office-C"])
            self.assertTrue(reading.HasField("ts"))

if __name__ == '__main__':
    unittest.main()
