import json
import logging
import os

import bottle
from bottle import TEMPLATE_PATH, Bottle, redirect, request, template

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

CONFIG_PATH = os.getenv("SENSOR_CONFIG_PATH", "./config/sensors.json")
ADMIN_HOST = os.getenv("ADMIN_HOST", "0.0.0.0")
ADMIN_PORT = int(os.getenv("ADMIN_PORT", 8080))

# Resolve views/ relative to this file so the app works from any working directory
TEMPLATE_PATH.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "views")
)

app = Bottle()

# Sensor types with their physical limits and form behaviour.
# Operational validation limits (used by service-2-go) are intentionally not defined here.
SENSOR_TYPES = {
    "temperature": {
        "label": "Temperature",
        "has_frequency": True,
        "default_frequency": 10,
        "thresholds": [
            {"label": "Physical range", "value": "-200 to 850 \u00b0C"},
        ],
    },
    "humidity": {
        "label": "Humidity",
        "has_frequency": True,
        "default_frequency": 15,
        "thresholds": [
            {"label": "Physical range", "value": "0 to 100 %RH"},
        ],
    },
    "gas": {
        "label": "Gas",
        "has_frequency": True,
        "default_frequency": 3,
        "thresholds": [
            {"label": "CO\u2082 physical range", "value": "0 to 50,000 ppm"},
            {"label": "LPG physical range", "value": "0 to 10,000 ppm"},
        ],
    },
    "door": {
        "label": "Door",
        "has_frequency": False,
        "behavior": "Sends on state change, or every 30 s as a keepalive.",
    },
    "alert": {
        "label": "Alert",
        "has_frequency": False,
        "behavior": "Every 1 s while alerting; every 60 s when idle.",
    },
}

# In-memory working state — loaded at startup, mutated by CRUD, flushed to disk on Apply.
_config: dict = {}
_dirty: bool = False  # True when in-memory state differs from the saved file


def _load_config() -> None:
    global _config, _dirty
    with open(CONFIG_PATH, "r") as f:
        _config = json.load(f)
    _dirty = False
    logging.info(
        f"Config loaded from {CONFIG_PATH} ({len(_config.get('sensors', []))} sensors)"
    )


def _save_config() -> None:
    """Write the in-memory config to disk, using a temp file to avoid partial writes."""
    global _dirty
    config_dir = os.path.dirname(CONFIG_PATH)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    tmp_path = CONFIG_PATH + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(_config, f, indent=2)
    os.replace(tmp_path, CONFIG_PATH)
    _dirty = False
    logging.info(f"Config saved to {CONFIG_PATH}")


def generate_sensor_id(sensor_type: str) -> str:
    """Return the next slug ID for a sensor type, e.g. sim-temperature-03."""
    counters = _config.setdefault("type_counters", {})
    counters[sensor_type] = counters.get(sensor_type, 0) + 1
    return f"sim-{sensor_type}-{counters[sensor_type]:02d}"


def _find_sensor(sensor_id: str) -> dict | None:
    for s in _config.get("sensors", []):
        if s["id"] == sensor_id:
            return s
    return None


def _validate_form(form: dict, is_edit: bool = False) -> tuple:
    """Validate form data. Returns (errors, parsed). On edit, inject sensor type before calling."""
    errors = []
    parsed = {}

    name = form.get("name", "").strip()
    location = form.get("location", "").strip()
    sensor_type = form.get("type", "").strip()

    if not name:
        errors.append("Sensor name is required.")
    if not location:
        errors.append("Location is required.")

    if not is_edit:
        if sensor_type not in SENSOR_TYPES:
            errors.append(f"Invalid sensor type: '{sensor_type}'.")
        parsed["type"] = sensor_type

    # Validate sample frequency only for types that use it
    if sensor_type in SENSOR_TYPES and SENSOR_TYPES[sensor_type]["has_frequency"]:
        freq_raw = form.get("sample_frequency_seconds", "").strip()
        try:
            freq = int(freq_raw)
            if freq <= 0:
                errors.append("Sample frequency must be a positive whole number.")
            else:
                parsed["sample_frequency_seconds"] = freq
        except (ValueError, TypeError):
            errors.append("Sample frequency must be a valid whole number.")

    parsed["name"] = name
    parsed["location"] = location
    return errors, parsed


@app.route("/")
def index():
    saved = request.query.get("saved") == "1"
    return template(
        "index",
        sensors=_config.get("sensors", []),
        sensor_types=SENSOR_TYPES,
        dirty=_dirty,
        saved=saved,
    )


@app.route("/sensors/new", method="GET")
def new_sensor_form():
    return template(
        "sensor_form",
        sensor=None,
        sensor_types=SENSOR_TYPES,
        errors=[],
        form_data={},
        title="Add Sensor",
    )


@app.route("/sensors/new", method="POST")
def create_sensor():
    global _dirty
    form = {k: request.forms.get(k) for k in request.forms}
    errors, parsed = _validate_form(form, is_edit=False)

    if errors:
        return template(
            "sensor_form",
            sensor=None,
            sensor_types=SENSOR_TYPES,
            errors=errors,
            form_data=form,
            title="Add Sensor",
        )

    new_sensor = {
        "id": generate_sensor_id(parsed["type"]),
        "name": parsed["name"],
        "type": parsed["type"],
        "location": parsed["location"],
    }
    if "sample_frequency_seconds" in parsed:
        new_sensor["sample_frequency_seconds"] = parsed["sample_frequency_seconds"]

    _config.setdefault("sensors", []).append(new_sensor)
    _dirty = True
    logging.info(f"Sensor created in memory: {new_sensor['id']}")
    redirect("/")


@app.route("/sensors/<sensor_id>/edit", method="GET")
def edit_sensor_form(sensor_id):
    sensor = _find_sensor(sensor_id)
    if sensor is None:
        bottle.abort(404, f"Sensor '{sensor_id}' not found.")
    return template(
        "sensor_form",
        sensor=sensor,
        sensor_types=SENSOR_TYPES,
        errors=[],
        form_data=sensor,
        title="Edit Sensor",
    )


@app.route("/sensors/<sensor_id>/edit", method="POST")
def update_sensor(sensor_id):
    global _dirty
    sensor = _find_sensor(sensor_id)
    if sensor is None:
        bottle.abort(404, f"Sensor '{sensor_id}' not found.")

    form = {k: request.forms.get(k) for k in request.forms}
    # Inject the existing type so frequency validation knows whether to fire
    form["type"] = sensor["type"]
    errors, parsed = _validate_form(form, is_edit=True)

    if errors:
        return template(
            "sensor_form",
            sensor=sensor,
            sensor_types=SENSOR_TYPES,
            errors=errors,
            form_data={**sensor, **form},
            title="Edit Sensor",
        )

    sensor["name"] = parsed["name"]
    sensor["location"] = parsed["location"]
    if "sample_frequency_seconds" in parsed:
        sensor["sample_frequency_seconds"] = parsed["sample_frequency_seconds"]
    elif "sample_frequency_seconds" in sensor:
        # Shouldn't happen, but guard against stale keys on type changes
        del sensor["sample_frequency_seconds"]

    _dirty = True
    logging.info(f"Sensor updated in memory: {sensor_id}")
    redirect("/")


@app.route("/sensors/<sensor_id>/delete", method="POST")
def delete_sensor(sensor_id):
    global _dirty
    sensors = _config.get("sensors", [])
    original_count = len(sensors)
    _config["sensors"] = [s for s in sensors if s["id"] != sensor_id]

    if len(_config["sensors"]) == original_count:
        bottle.abort(404, f"Sensor '{sensor_id}' not found.")

    _dirty = True
    logging.info(f"Sensor deleted from memory: {sensor_id}")
    redirect("/")


@app.route("/apply", method="POST")
def apply_config():
    if _dirty:
        _save_config()
    redirect("/?saved=1")


if __name__ == "__main__":
    _load_config()
    app.run(host=ADMIN_HOST, port=ADMIN_PORT, debug=False, reloader=False)
