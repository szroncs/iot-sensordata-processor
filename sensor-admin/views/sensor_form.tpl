% import json
% is_edit       = sensor is not None
% action        = f"/sensors/{sensor['id']}/edit" if is_edit else "/sensors/new"
% current_type  = sensor['type'] if is_edit else form_data.get('type', '')
% type_def      = sensor_types.get(current_type, {})
% show_freq     = type_def.get('has_frequency', False) if current_type else True
% show_thresh   = bool(current_type)
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{title}} — IoT Sensor Admin</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #f8f9fa; }
    .threshold-row { display: flex; justify-content: space-between; padding: 2px 0; }
  </style>
</head>
<body>
<nav class="navbar navbar-dark bg-dark mb-4">
  <div class="container">
    <span class="navbar-brand mb-0 h1">&#128268; IoT Sensor Admin</span>
  </div>
</nav>

<div class="container pb-5" style="max-width: 640px;">

  <!-- breadcrumb -->
  <nav aria-label="breadcrumb" class="mb-3">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/">Sensor Admin</a></li>
      <li class="breadcrumb-item active">{{title}}</li>
    </ol>
  </nav>

  <div class="card shadow-sm">
    <div class="card-header">
      <h2 class="h5 mb-0">{{title}}</h2>
    </div>
    <div class="card-body">

      <!-- ── Validation errors ─────────────────────────────────────────────── -->
      % if errors:
      <div class="alert alert-danger">
        <ul class="mb-0 ps-3">
          % for err in errors:
          <li>{{err}}</li>
          % end
        </ul>
      </div>
      % end

      <form action="{{action}}" method="post">

        <!-- Sensor ID (read-only on edit) -->
        % if is_edit:
        <div class="mb-3">
          <label class="form-label fw-semibold">Sensor ID</label>
          <input type="text" class="form-control form-control-sm bg-light"
                 value="{{sensor['id']}}" disabled>
          <div class="form-text">Auto-generated slug. Cannot be changed.</div>
        </div>
        % end

        <!-- Name -->
        <div class="mb-3">
          <label for="name" class="form-label fw-semibold">
            Name <span class="text-danger">*</span>
          </label>
          <input type="text" class="form-control" id="name" name="name"
                 value="{{form_data.get('name', '')}}"
                 placeholder="e.g. Warehouse Temperature Sensor"
                 required autofocus>
        </div>

        <!-- Type (select on add, read-only badge on edit) -->
        <div class="mb-3">
          <label for="type" class="form-label fw-semibold">
            Type <span class="text-danger">*</span>
          </label>
          % if is_edit:
          <div>
            <span class="badge bg-secondary fs-6">{{type_def.get('label', sensor['type'])}}</span>
          </div>
          <div class="form-text">Sensor type cannot be changed after creation.</div>
          % else:
          <select class="form-select" id="type" name="type"
                  onchange="onTypeChange(this.value)" required>
            <option value="" disabled
                    {{"" if current_type else "selected"}}>Select a type…</option>
            % for type_key, tdef in sensor_types.items():
            <option value="{{type_key}}"
                    {{"selected" if current_type == type_key else ""}}>
              {{tdef['label']}}
            </option>
            % end
          </select>
          % end
        </div>

        <!-- Location -->
        <div class="mb-3">
          <label for="location" class="form-label fw-semibold">
            Location <span class="text-danger">*</span>
          </label>
          <input type="text" class="form-control" id="location" name="location"
                 value="{{form_data.get('location', '')}}"
                 placeholder="e.g. Warehouse-B" required>
        </div>

        <!-- Sample Frequency (hidden for door/alert) -->
        <div class="mb-3" id="freq-group"
             style="{{'display:none' if not show_freq else ''}}">
          <label for="sample_frequency_seconds" class="form-label fw-semibold">
            Sample Frequency <span class="text-danger">*</span>
          </label>
          <div class="input-group" style="max-width: 200px;">
            <input type="number" class="form-control" id="sample_frequency_seconds"
                   name="sample_frequency_seconds" min="1"
                   value="{{form_data.get('sample_frequency_seconds', '')}}">
            <span class="input-group-text">seconds</span>
          </div>
          <div class="form-text">How often this sensor publishes a reading.</div>
        </div>

        <!-- Sensor Threshold panel (read-only; physical hardware limits) -->
        <div class="mb-4 p-3 border rounded bg-light" id="threshold-panel"
             style="{{'display:none' if not show_thresh else ''}}">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="fw-semibold small text-uppercase text-secondary tracking-wide">
              Sensor Thresholds
            </span>
            <span class="badge bg-light text-secondary border">read-only</span>
          </div>
          <div id="threshold-content">
            <!-- Server-side initial render for SSR / JS-disabled fallback -->
            % if current_type and type_def.get('has_frequency'):
              % for t in type_def.get('thresholds', []):
              <div class="threshold-row">
                <span class="text-muted small">{{t['label']}}</span>
                <code class="small">{{t['value']}}</code>
              </div>
              % end
            % elif current_type:
              <span class="text-muted small fst-italic">
                {{type_def.get('behavior', '')}}
              </span>
            % end
          </div>
          <div class="form-text mt-2">
            Physical hardware limits &mdash; defined by sensor type and not configurable.
            These constrain the simulated values; they are distinct from the operational
            <em>sensor limits</em> used for validation in the processing pipeline.
          </div>
        </div>

        <!-- Actions -->
        <div class="d-flex gap-2">
          <button type="submit" class="btn btn-primary">
            &#10003; Save
          </button>
          <a href="/" class="btn btn-outline-secondary">Cancel</a>
        </div>

      </form>
    </div>
  </div>
</div>

<!-- Pass the type catalogue to JavaScript for dynamic UI updates -->
<script>
const SENSOR_TYPES = {{!json.dumps(sensor_types)}};

function onTypeChange(typeKey) {
  const def        = SENSOR_TYPES[typeKey];
  const freqGroup  = document.getElementById('freq-group');
  const thPanel    = document.getElementById('threshold-panel');
  const thContent  = document.getElementById('threshold-content');

  if (!def) return;

  // Show/hide the frequency input
  freqGroup.style.display = def.has_frequency ? '' : 'none';

  // Always show the threshold panel once a type is chosen
  thPanel.style.display = '';

  if (def.has_frequency && def.thresholds && def.thresholds.length) {
    thContent.innerHTML = def.thresholds.map(t =>
      `<div class="threshold-row">
         <span class="text-muted small">${t.label}</span>
         <code class="small">${t.value}</code>
       </div>`
    ).join('');
  } else if (def.behavior) {
    thContent.innerHTML =
      `<span class="text-muted small fst-italic">${def.behavior}</span>`;
  } else {
    thContent.innerHTML = '';
  }
}

// Re-trigger on page load when a type is already selected
// (covers: edit page, and add page re-rendered after a validation error)
% if current_type:
onTypeChange("{{current_type}}");
% end
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
