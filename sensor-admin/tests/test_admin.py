"""
Unit tests for sensor-admin/app.py.

Tests cover pure-logic functions only (no HTTP layer):
  - generate_sensor_id
  - _validate_form
  - _find_sensor
  - _load_config / _save_config (config I/O)

The Bottle dev server is intentionally not exercised here.
"""

import json
import os
import sys
import tempfile
import unittest

# Add the sensor-admin directory to the path so we can import app.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# app.py calls _load_config() only inside `if __name__ == '__main__':`,
# so importing it here is safe — no file I/O happens at import time.
import app as admin_app

# ── Helpers ───────────────────────────────────────────────────────────────────


def _blank_config() -> dict:
    return {"type_counters": {}, "sensors": []}


def _reset_state(sensors: list | None = None) -> None:
    """Reset the admin module's in-memory state before each test."""
    admin_app._config = _blank_config()
    if sensors:
        admin_app._config["sensors"] = sensors
    admin_app._temp_state = False


# ── generate_sensor_id ────────────────────────────────────────────────────────


class TestGenerateSensorId(unittest.TestCase):
    def setUp(self):
        _reset_state()

    def test_first_id_ends_with_01(self):
        sensor_id = admin_app.generate_sensor_id("temperature")
        self.assertEqual(sensor_id, "sim-temperature-01")

    def test_second_call_increments_counter(self):
        admin_app.generate_sensor_id("temperature")
        sensor_id = admin_app.generate_sensor_id("temperature")
        self.assertEqual(sensor_id, "sim-temperature-02")

    def test_counters_are_independent_per_type(self):
        t1 = admin_app.generate_sensor_id("temperature")
        h1 = admin_app.generate_sensor_id("humidity")
        t2 = admin_app.generate_sensor_id("temperature")
        self.assertEqual(t1, "sim-temperature-01")
        self.assertEqual(h1, "sim-humidity-01")
        self.assertEqual(t2, "sim-temperature-02")

    def test_counter_continues_after_sensor_deletion(self):
        """
        IDs must never be reused: even if sensors are deleted the counter
        keeps incrementing so historical InfluxDB data stays unambiguous.
        """
        admin_app._config["type_counters"] = {"temperature": 3}
        sensor_id = admin_app.generate_sensor_id("temperature")
        self.assertEqual(sensor_id, "sim-temperature-04")

    def test_single_digit_values_are_zero_padded(self):
        admin_app._config["type_counters"] = {"gas": 8}
        self.assertEqual(admin_app.generate_sensor_id("gas"), "sim-gas-09")

    def test_counter_beyond_99_is_not_truncated(self):
        admin_app._config["type_counters"] = {"door": 99}
        self.assertEqual(admin_app.generate_sensor_id("door"), "sim-door-100")

    def test_new_type_with_no_prior_counter(self):
        # 'alert' has never been generated — counter must start from 0 → produce 01
        sensor_id = admin_app.generate_sensor_id("alert")
        self.assertEqual(sensor_id, "sim-alert-01")

    def test_counter_is_persisted_in_config(self):
        admin_app.generate_sensor_id("humidity")
        self.assertEqual(admin_app._config["type_counters"]["humidity"], 1)


# ── _validate_form ────────────────────────────────────────────────────────────


class TestValidateForm(unittest.TestCase):
    def _base_form(self, overrides: dict | None = None) -> dict:
        form = {
            "name": "My Sensor",
            "type": "temperature",
            "location": "Lab-A",
            "sample_frequency_seconds": "10",
        }
        if overrides:
            form.update(overrides)
        return form

    # ── happy path ──────────────────────────────────────────────────────────

    def test_valid_temperature_form_no_errors(self):
        errors, parsed = admin_app._validate_form(self._base_form())
        self.assertEqual(errors, [])

    def test_parsed_name_and_location_are_stripped(self):
        form = self._base_form({"name": "  Sensor  ", "location": "  Room  "})
        _, parsed = admin_app._validate_form(form)
        self.assertEqual(parsed["name"], "Sensor")
        self.assertEqual(parsed["location"], "Room")

    def test_parsed_frequency_is_integer(self):
        _, parsed = admin_app._validate_form(self._base_form())
        self.assertIsInstance(parsed["sample_frequency_seconds"], int)
        self.assertEqual(parsed["sample_frequency_seconds"], 10)

    def test_valid_humidity_form(self):
        form = self._base_form({"type": "humidity", "sample_frequency_seconds": "15"})
        errors, _ = admin_app._validate_form(form)
        self.assertEqual(errors, [])

    def test_valid_gas_form(self):
        form = self._base_form({"type": "gas", "sample_frequency_seconds": "3"})
        errors, _ = admin_app._validate_form(form)
        self.assertEqual(errors, [])

    def test_door_sensor_requires_no_frequency(self):
        form = {"name": "Door", "type": "door", "location": "Entrance"}
        errors, parsed = admin_app._validate_form(form)
        self.assertEqual(errors, [])
        self.assertNotIn("sample_frequency_seconds", parsed)

    def test_alert_sensor_requires_no_frequency(self):
        form = {"name": "Alert", "type": "alert", "location": "Floor"}
        errors, parsed = admin_app._validate_form(form)
        self.assertEqual(errors, [])
        self.assertNotIn("sample_frequency_seconds", parsed)

    # ── required field validation ────────────────────────────────────────────

    def test_empty_name_is_rejected(self):
        errors, _ = admin_app._validate_form(self._base_form({"name": ""}))
        self.assertTrue(any("name" in e.lower() for e in errors))

    def test_whitespace_only_name_is_rejected(self):
        errors, _ = admin_app._validate_form(self._base_form({"name": "   "}))
        self.assertTrue(any("name" in e.lower() for e in errors))

    def test_empty_location_is_rejected(self):
        errors, _ = admin_app._validate_form(self._base_form({"location": ""}))
        self.assertTrue(any("location" in e.lower() for e in errors))

    def test_invalid_type_is_rejected_on_create(self):
        errors, _ = admin_app._validate_form(self._base_form({"type": "unknown"}))
        self.assertTrue(any("type" in e.lower() or "Invalid" in e for e in errors))

    # ── frequency validation ─────────────────────────────────────────────────

    def test_zero_frequency_is_rejected(self):
        errors, _ = admin_app._validate_form(
            self._base_form({"sample_frequency_seconds": "0"})
        )
        self.assertTrue(any("frequency" in e.lower() for e in errors))

    def test_negative_frequency_is_rejected(self):
        errors, _ = admin_app._validate_form(
            self._base_form({"sample_frequency_seconds": "-5"})
        )
        self.assertTrue(any("frequency" in e.lower() for e in errors))

    def test_non_integer_frequency_is_rejected(self):
        errors, _ = admin_app._validate_form(
            self._base_form({"sample_frequency_seconds": "1.5"})
        )
        self.assertTrue(any("frequency" in e.lower() for e in errors))

    def test_alphabetic_frequency_is_rejected(self):
        errors, _ = admin_app._validate_form(
            self._base_form({"sample_frequency_seconds": "abc"})
        )
        self.assertTrue(any("frequency" in e.lower() for e in errors))

    def test_missing_frequency_for_temperature_is_rejected(self):
        form = self._base_form({"sample_frequency_seconds": ""})
        errors, _ = admin_app._validate_form(form)
        self.assertTrue(any("frequency" in e.lower() for e in errors))

    # ── edit mode ────────────────────────────────────────────────────────────

    def test_edit_mode_skips_type_validation(self):
        """
        On edit, the type field is pre-injected by the route and must not
        trigger a type-not-in-SENSOR_TYPES error even if the value is unusual.
        """
        form = {
            "name": "Updated",
            "type": "temperature",
            "location": "New Place",
            "sample_frequency_seconds": "5",
        }
        errors, _ = admin_app._validate_form(form, is_edit=True)
        self.assertEqual(errors, [])

    def test_edit_mode_does_not_return_type_in_parsed(self):
        form = {
            "name": "Updated",
            "type": "temperature",
            "location": "New Place",
            "sample_frequency_seconds": "5",
        }
        _, parsed = admin_app._validate_form(form, is_edit=True)
        self.assertNotIn("type", parsed)

    def test_multiple_errors_are_accumulated(self):
        form = {
            "name": "",
            "type": "bad",
            "location": "",
            "sample_frequency_seconds": "nope",
        }
        errors, _ = admin_app._validate_form(form)
        # At minimum: name, location, type, frequency → ≥ 3 errors
        self.assertGreaterEqual(len(errors), 3)


# ── _find_sensor ──────────────────────────────────────────────────────────────


class TestFindSensor(unittest.TestCase):
    def setUp(self):
        _reset_state(
            [
                {
                    "id": "sim-temperature-01",
                    "name": "T1",
                    "type": "temperature",
                    "location": "A",
                    "sample_frequency_seconds": 10,
                },
                {"id": "sim-door-01", "name": "D1", "type": "door", "location": "B"},
            ]
        )

    def test_finds_existing_sensor_by_id(self):
        s = admin_app._find_sensor("sim-temperature-01")
        self.assertIsNotNone(s)
        self.assertEqual(s["name"], "T1")

    def test_finds_second_sensor(self):
        s = admin_app._find_sensor("sim-door-01")
        self.assertIsNotNone(s)
        self.assertEqual(s["type"], "door")

    def test_returns_none_for_missing_id(self):
        self.assertIsNone(admin_app._find_sensor("sim-nonexistent-99"))

    def test_returns_none_on_empty_sensor_list(self):
        _reset_state([])
        self.assertIsNone(admin_app._find_sensor("sim-temperature-01"))


# ── Config I/O ────────────────────────────────────────────────────────────────


class TestConfigIO(unittest.TestCase):
    def _write_json(self, data: dict) -> str:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, tmp)
        tmp.close()
        return tmp.name

    def test_load_config_populates_global_state(self):
        data = {
            "type_counters": {"temperature": 2},
            "sensors": [
                {
                    "id": "sim-temperature-01",
                    "name": "T1",
                    "type": "temperature",
                    "location": "Lab",
                    "sample_frequency_seconds": 10,
                },
                {
                    "id": "sim-temperature-02",
                    "name": "T2",
                    "type": "temperature",
                    "location": "Office",
                    "sample_frequency_seconds": 5,
                },
            ],
        }
        path = self._write_json(data)
        original_path = admin_app.CONFIG_PATH
        admin_app.CONFIG_PATH = path
        try:
            admin_app._load_config()
            self.assertEqual(len(admin_app._config["sensors"]), 2)
            self.assertEqual(admin_app._config["type_counters"]["temperature"], 2)
            self.assertFalse(admin_app._temp_state)
        finally:
            admin_app.CONFIG_PATH = original_path
            os.unlink(path)

    def test_save_config_writes_valid_json(self):
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir, "sensors.json")
        _reset_state(
            [
                {
                    "id": "sim-humidity-01",
                    "name": "H1",
                    "type": "humidity",
                    "location": "B",
                    "sample_frequency_seconds": 15,
                },
            ]
        )
        admin_app._temp_state = True
        original_path = admin_app.CONFIG_PATH
        admin_app.CONFIG_PATH = path
        try:
            admin_app._save_config()
            self.assertTrue(os.path.exists(path))
            self.assertFalse(admin_app._temp_state)
            with open(path) as f:
                saved = json.load(f)
            self.assertEqual(saved["sensors"][0]["id"], "sim-humidity-01")
        finally:
            admin_app.CONFIG_PATH = original_path
            if os.path.exists(path):
                os.unlink(path)
            os.rmdir(tmp_dir)

    def test_save_config_does_not_leave_tmp_file(self):
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir, "sensors.json")
        _reset_state()
        admin_app._temp_state = True
        original_path = admin_app.CONFIG_PATH
        admin_app.CONFIG_PATH = path
        try:
            admin_app._save_config()
            self.assertFalse(os.path.exists(path + ".tmp"))
        finally:
            admin_app.CONFIG_PATH = original_path
            if os.path.exists(path):
                os.unlink(path)
            os.rmdir(tmp_dir)

    def test_save_config_clears_dirty_flag(self):
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir, "sensors.json")
        _reset_state()
        admin_app._temp_state = True
        original_path = admin_app.CONFIG_PATH
        admin_app.CONFIG_PATH = path
        try:
            admin_app._save_config()
            self.assertFalse(admin_app._temp_state)
        finally:
            admin_app.CONFIG_PATH = original_path
            if os.path.exists(path):
                os.unlink(path)
            os.rmdir(tmp_dir)


if __name__ == "__main__":
    unittest.main()
