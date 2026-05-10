<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>IoT Sensor Admin</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #f8f9fa; }
    code { font-size: .875em; }
  </style>
</head>
<body>
<nav class="navbar navbar-dark bg-dark mb-4">
  <div class="container">
    <span class="navbar-brand mb-0 h1">&#128268; IoT Sensor Admin</span>
  </div>
</nav>

<div class="container pb-5" style="max-width: 960px;">

  <!-- Status banners -->
  % if saved:
  <div class="alert alert-success alert-dismissible fade show d-flex align-items-center gap-2" role="alert">
    <span>&#9989;</span>
    <div>
      <strong>Configuration saved.</strong>
      Restart the simulator to apply:
      <code>podman-compose restart service-1-python</code>
    </div>
    <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
  </div>
  % end

  % if dirty:
  <div class="alert alert-warning d-flex align-items-center gap-2" role="alert">
    <span>&#9888;&#65039;</span>
    <div>
      <strong>You have unsaved changes.</strong>
      Click <strong>Apply Configuration</strong> to write them to disk.
    </div>
  </div>
  % end

  <!-- Header row -->
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h2 class="h5 mb-0 text-secondary">
      Configured Sensors
      <span class="badge bg-secondary fw-normal ms-1">{{len(sensors)}}</span>
    </h2>
    <div class="d-flex gap-2">
      <form action="/apply" method="post" class="mb-0">
        <button type="submit" class="btn btn-success btn-sm"
                {{"" if dirty else "disabled"}}
                title="{{"Save changes to disk" if dirty else "No unsaved changes"}}">
          &#10003; Apply Configuration
        </button>
      </form>
      <a href="/sensors/new" class="btn btn-primary btn-sm">&#43; Add Sensor</a>
    </div>
  </div>

  <!-- Sensor table -->
  <div class="card shadow-sm">
    % if sensors:
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th scope="col" class="text-nowrap">Sensor ID</th>
            <th scope="col">Name</th>
            <th scope="col">Type</th>
            <th scope="col">Location</th>
            <th scope="col" class="text-nowrap">Sample Frequency</th>
            <th scope="col" class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          % for sensor in sensors:
          % type_def = sensor_types.get(sensor['type'], {})
          <tr>
            <td><code>{{sensor['id']}}</code></td>
            <td>{{sensor['name']}}</td>
            <td>
              <span class="badge bg-secondary">{{type_def.get('label', sensor['type'])}}</span>
            </td>
            <td>{{sensor['location']}}</td>
            <td>
              % if type_def.get('has_frequency'):
                <span class="fw-semibold">{{sensor.get('sample_frequency_seconds', '—')}}</span>
                <span class="text-muted small">s</span>
              % else:
                <span class="text-muted fst-italic small">
                  {{type_def.get('behavior', 'Predefined')}}
                </span>
              % end
            </td>
            <td class="text-end text-nowrap">
              <a href="/sensors/{{sensor['id']}}/edit"
                 class="btn btn-sm btn-outline-secondary">Edit</a>
              <form action="/sensors/{{sensor['id']}}/delete"
                    method="post" class="d-inline"
                    onsubmit="return confirm('Delete sensor {{sensor['id']}}?')">
                <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
              </form>
            </td>
          </tr>
          % end
        </tbody>
      </table>
    </div>
    % else:
    <div class="card-body text-center text-muted py-5">
      <p class="mb-2">&#128268; No sensors configured yet.</p>
      <a href="/sensors/new" class="btn btn-primary btn-sm">Add your first sensor</a>
    </div>
    % end
  </div>

  <!-- Legend -->
  <div class="mt-4 text-muted small">
    <strong>Note:</strong>
    Changes are held in memory until you click <em>Apply Configuration</em>.
    After applying, restart <code>service-1-python</code> for them to take effect.
    Door and Alert sensors use predefined publish intervals that are not user-configurable.
  </div>

</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
