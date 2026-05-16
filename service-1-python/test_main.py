import json
import os
import sys
import tempfile
import unittest

# Make the generated protobuf bindings importable
sys.path.append(os.path.join(os.path.dirname(__file__), "gen", "iot_pb"))

import sensor_pb2
from main import (
    SensorState,
    load_sensor_config,
    simulate_alert,
    simulate_door,
    simulate_gas,
    simulate_humidity,
    simulate_temperature,
)


class TestSimulateTemperature(unittest.TestCase):
    def test_returns_correct_type(self):
        self.assertIsInstance(simulate_temperature(), sensor_pb2.TemperatureReading)

    def test_value_within_physical_bounds(self):
        """Run many samples to exercise the Gaussian tail; all must be clamped."""
        for _ in range(200):
            reading = simulate_temperature()
            self.assertGreaterEqual(reading.value, -200.0)
            self.assertLessEqual(reading.value, 850.0)

    def test_value_rounded_to_two_decimal_places(self):
        # Protobuf `float` is 32-bit and python uses float 64
        # for the simulation we are completely fine with 2 decimal precision which mitigates the float discrepancy
        reading = simulate_temperature()
        self.assertAlmostEqual(reading.value, round(reading.value, 2), places=4)


class TestSimulateHumidity(unittest.TestCase):
    def test_returns_correct_type(self):
        self.assertIsInstance(simulate_humidity(), sensor_pb2.HumidityReading)

    def test_value_within_physical_bounds(self):
        for _ in range(200):
            reading = simulate_humidity()
            self.assertGreaterEqual(reading.value, 0.0)
            self.assertLessEqual(reading.value, 100.0)

    def test_value_rounded_to_two_decimal_places(self):
        reading = simulate_humidity()
        self.assertAlmostEqual(reading.value, round(reading.value, 2), places=4)


class TestSimulateGas(unittest.TestCase):
    def test_returns_correct_type(self):
        self.assertIsInstance(simulate_gas(), sensor_pb2.GasReading)

    def test_co2_within_physical_bounds(self):
        for _ in range(200):
            reading = simulate_gas()
            self.assertGreaterEqual(reading.co2_ppm, 0.0)
            self.assertLessEqual(reading.co2_ppm, 50000.0)

    def test_lpg_within_physical_bounds(self):
        for _ in range(200):
            reading = simulate_gas()
            self.assertGreaterEqual(reading.lpg_presence, 0.0)
            self.assertLessEqual(reading.lpg_presence, 10000.0)

    def test_both_fields_rounded(self):
        reading = simulate_gas()
        self.assertAlmostEqual(reading.co2_ppm, round(reading.co2_ppm, 2), places=4)
        self.assertAlmostEqual(
            reading.lpg_presence, round(reading.lpg_presence, 2), places=4
        )


class TestSimulateDoor(unittest.TestCase):
    def test_returns_correct_type(self):
        self.assertIsInstance(simulate_door(True), sensor_pb2.DoorReading)

    def test_open_state_reflected(self):
        self.assertTrue(simulate_door(True).is_open)

    def test_closed_state_reflected(self):
        self.assertFalse(simulate_door(False).is_open)


class TestSimulateAlert(unittest.TestCase):
    def test_returns_correct_type(self):
        reading = simulate_alert(True, sensor_pb2.AlertReading.SEVERITY_INFO)
        self.assertIsInstance(reading, sensor_pb2.AlertReading)

    def test_active_flag_set(self):
        reading = simulate_alert(True, sensor_pb2.AlertReading.SEVERITY_WARNING)
        self.assertTrue(reading.active)

    def test_inactive_flag_set(self):
        reading = simulate_alert(False, sensor_pb2.AlertReading.SEVERITY_INFO)
        self.assertFalse(reading.active)

    def test_severity_info(self):
        reading = simulate_alert(True, sensor_pb2.AlertReading.SEVERITY_INFO)
        self.assertEqual(reading.severity, sensor_pb2.AlertReading.SEVERITY_INFO)

    def test_severity_warning(self):
        reading = simulate_alert(True, sensor_pb2.AlertReading.SEVERITY_WARNING)
        self.assertEqual(reading.severity, sensor_pb2.AlertReading.SEVERITY_WARNING)

    def test_severity_critical(self):
        reading = simulate_alert(True, sensor_pb2.AlertReading.SEVERITY_CRITICAL)
        self.assertEqual(reading.severity, sensor_pb2.AlertReading.SEVERITY_CRITICAL)


# Config tests


class TestLoadSensorConfig(unittest.TestCase):
    def _write_config(self, data: dict) -> str:
        """Write a dict to a temp JSON file and return its path."""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, tmp)
        tmp.close()
        return tmp.name

    def _valid_config(self, sensors: list) -> dict:
        return {"type_counters": {}, "sensors": sensors}

    def test_returns_list_of_sensors(self):
        path = self._write_config(
            self._valid_config(
                [
                    {
                        "id": "sim-temperature-01",
                        "name": "T1",
                        "type": "temperature",
                        "location": "Lab",
                        "sample_frequency_seconds": 10,
                    },
                ]
            )
        )
        sensors = load_sensor_config(path)
        self.assertIsInstance(sensors, list)
        self.assertEqual(len(sensors), 1)
        os.unlink(path)

    def test_loads_all_sensor_fields(self):
        sensor = {
            "id": "sim-humidity-01",
            "name": "H1",
            "type": "humidity",
            "location": "Room-A",
            "sample_frequency_seconds": 15,
        }
        path = self._write_config(self._valid_config([sensor]))
        sensors = load_sensor_config(path)
        self.assertEqual(sensors[0]["id"], "sim-humidity-01")
        self.assertEqual(sensors[0]["location"], "Room-A")
        self.assertEqual(sensors[0]["sample_frequency_seconds"], 15)
        os.unlink(path)

    def test_loads_multiple_sensors(self):
        path = self._write_config(
            self._valid_config(
                [
                    {
                        "id": "sim-temperature-01",
                        "name": "T",
                        "type": "temperature",
                        "location": "A",
                        "sample_frequency_seconds": 10,
                    },
                    {"id": "sim-door-01", "name": "D", "type": "door", "location": "B"},
                    {
                        "id": "sim-alert-01",
                        "name": "AL",
                        "type": "alert",
                        "location": "C",
                    },
                ]
            )
        )
        sensors = load_sensor_config(path)
        self.assertEqual(len(sensors), 3)
        os.unlink(path)

    def test_door_sensor_has_no_frequency_key(self):
        path = self._write_config(
            self._valid_config(
                [
                    {
                        "id": "sim-door-01",
                        "name": "Door",
                        "type": "door",
                        "location": "Entrance",
                    },
                ]
            )
        )
        sensors = load_sensor_config(path)
        self.assertNotIn("sample_frequency_seconds", sensors[0])
        os.unlink(path)

    def test_alert_sensor_has_no_frequency_key(self):
        path = self._write_config(
            self._valid_config(
                [
                    {
                        "id": "sim-alert-01",
                        "name": "Alert",
                        "type": "alert",
                        "location": "Floor",
                    },
                ]
            )
        )
        sensors = load_sensor_config(path)
        self.assertNotIn("sample_frequency_seconds", sensors[0])
        os.unlink(path)

    def test_empty_sensors_list_is_valid(self):
        path = self._write_config({"type_counters": {}, "sensors": []})
        sensors = load_sensor_config(path)
        self.assertEqual(sensors, [])
        os.unlink(path)

    def test_missing_file_causes_exit(self):
        with self.assertRaises(SystemExit):
            load_sensor_config("/nonexistent/path/sensors.json")

    def test_malformed_json_causes_exit(self):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        tmp.write("{ this is not valid json }")
        tmp.close()
        with self.assertRaises(SystemExit):
            load_sensor_config(tmp.name)
        os.unlink(tmp.name)


# SensorState tests


class TestSensorStateInit(unittest.TestCase):
    def _make_state(self, sensor_type: str, **extra) -> SensorState:
        cfg = {"id": f"sim-{sensor_type}-01", "type": sensor_type, "location": "A"}
        cfg.update(extra)
        return SensorState(cfg)

    def test_common_fields_initialised(self):
        state = self._make_state("temperature", sample_frequency_seconds=10)
        self.assertEqual(state.last_publish, 0.0)
        self.assertIs(state.config["type"], "temperature")

    def test_temperature_has_no_type_specific_state(self):
        state = self._make_state("temperature", sample_frequency_seconds=10)
        self.assertFalse(hasattr(state, "door_is_open"))
        self.assertFalse(hasattr(state, "alert_is_active"))

    def test_humidity_has_no_type_specific_state(self):
        state = self._make_state("humidity", sample_frequency_seconds=15)
        self.assertFalse(hasattr(state, "door_is_open"))
        self.assertFalse(hasattr(state, "alert_is_active"))

    def test_gas_has_no_type_specific_state(self):
        state = self._make_state("gas", sample_frequency_seconds=3)
        self.assertFalse(hasattr(state, "door_is_open"))
        self.assertFalse(hasattr(state, "alert_is_active"))

    def test_door_state_initialised_closed(self):
        state = self._make_state("door")
        self.assertFalse(state.door_is_open)
        self.assertEqual(state.last_publish, 0.0)

    def test_alert_state_initialised_inactive(self):
        state = self._make_state("alert")
        self.assertFalse(state.alert_is_active)
        self.assertEqual(state.alert_start_time, 0.0)
        self.assertEqual(state.alert_severity, sensor_pb2.AlertReading.SEVERITY_INFO)


if __name__ == "__main__":
    unittest.main()
