<script setup>
const form = reactive({
  device_id: '',
  device_type: '',
  location: '',
  pipeline: 'generic_iot',
  description: '',
  metrics: [
    {
      metric_name: '',
      metric_unit: '',
      description: ''
    }
  ]
})

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

async function registerDevice() {
  successMessage.value = ''
  errorMessage.value = ''

  loading.value = true

  try {
    const config = useRuntimeConfig()

    const response = await $fetch(
      `${config.public.apiBase}/devices`,
      {
        method: 'POST',
        body: form
      }
    )

    successMessage.value = response.message

    form.device_id = ''
    form.device_type = ''
    form.location = ''
    form.pipeline = 'generic_iot'
    form.description = ''

    form.metrics = [
      {
        metric_name: '',
        metric_unit: '',
        description: ''
      }
    ]
  }

  catch (err) {
    errorMessage.value =
      err?.data?.detail ||
      'Failed to register device'
  }

  finally {
    loading.value = false
  }
}

function addMetric() {
  form.metrics.push({
    metric_name: '',
    metric_unit: '',
    description: ''
  })
}

function removeMetric(index) {
  form.metrics.splice(index, 1)
}
</script>

<template>
  <div class="container">

    <h1>IoT Device Registry</h1>
    <p class="subtitle">
      Register MQTT-connected scientific and IoT devices
      into the Radxa telemetry infrastructure.
    </p>

    <form @submit.prevent="registerDevice">

      <div class="field">
        <label>Device ID</label>

        <input
          v-model="form.device_id"
          placeholder="coac_2"
          required
        />
      </div>

      <div class="field">
        <label>Device Type</label>

        <input
          v-model="form.device_type"
          placeholder="solar_monitor"
          required
        />
      </div>

      <div class="field">
        <label>Location</label>

        <input
          v-model="form.location"
          placeholder="Rooftop"
          required
        />
      </div>

      <div class="field">
        <label>Pipeline</label>

        <select v-model="form.pipeline">

          <option value="solar_monitoring">
            Solar COAC → monitoring
          </option>

          <option value="generic_iot">
            Generic IoT → iot_measurements
          </option>

        </select>
      </div>

      <div class="field">
        <label>Description</label>

        <textarea
          v-model="form.description"
          rows="3"
        />
      </div>

      <hr>

      <h2>Metrics</h2>

      <div
        v-for="(metric, index) in form.metrics"
        :key="index"
        class="metric-card"
      >

        <div class="field">
          <label>Metric Name</label>

          <input
            v-model="metric.metric_name"
            placeholder="temperature"
            required
          />
        </div>

        <div class="field">
          <label>Metric Unit</label>

          <input
            v-model="metric.metric_unit"
            placeholder="°C"
            required
          />
        </div>

        <div class="field">
          <label>Description</label>

          <input
            v-model="metric.description"
            placeholder="Ambient temperature"
          />
        </div>

        <button
          type="button"
          class="remove-btn"
          @click="removeMetric(index)"
          v-if="form.metrics.length > 1"
        >
          Remove Metric
        </button>

      </div>

      <button
        type="button"
        class="add-btn"
        @click="addMetric"
      >
        Add Metric
      </button>

      <hr>

      <button
        type="submit"
        class="submit-btn"
        :disabled="loading"
      >
        {{ loading ? 'Registering...' : 'Register Device' }}
      </button>

    </form>

    <div
      v-if="successMessage"
      class="success"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage"
      class="error"
    >
      {{ errorMessage }}
    </div>

  </div>
</template>

<style>
:root {
  --bg: #f4f7f9;
  --card: #ffffff;
  --border: #dce3e8;

  --text: #1f2933;
  --muted: #6b7280;

  --accent: #19c37d;
  --accent-hover: #14a46a;

  --danger: #dc2626;
  --success: #15803d;

  --shadow:
    0 4px 12px rgba(0, 0, 0, 0.05);

  font-family:
    Inter,
    Arial,
    sans-serif;
}

body {
  margin: 0;
  background:
    linear-gradient(
      180deg,
      #eef3f6 0%,
      #f8fafb 100%
    );

  color: var(--text);
}

.container {
  max-width: 980px;
  margin: auto;
  padding: 3rem 1.5rem;
}

h1 {
  font-size: 2.2rem;
  margin-bottom: 0.4rem;
  letter-spacing: -0.03em;
}

h2 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-size: 1.4rem;
}

.subtitle {
  color: var(--muted);
  margin-bottom: 2rem;
}

form {
  background: var(--card);
  padding: 2rem;
  border-radius: 18px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.field {
  margin-bottom: 1.3rem;
}

label {
  display: block;
  margin-bottom: 0.45rem;
  font-weight: 600;
  color: var(--text);
}

input,
textarea,
select {
  width: 100%;
  padding: 0.85rem 1rem;

  border-radius: 12px;
  border: 1px solid #ccd5db;

  font-size: 0.95rem;
  background: white;

  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;

  border-color: var(--accent);

  box-shadow:
    0 0 0 4px rgba(25, 195, 125, 0.15);
}

.metric-card {
  background:
    linear-gradient(
      180deg,
      #fbfcfd 0%,
      #f5f8fa 100%
    );

  padding: 1.4rem;

  border-radius: 16px;

  border: 1px solid var(--border);

  margin-bottom: 1rem;
}

button {
  cursor: pointer;
  transition:
    transform 0.15s,
    opacity 0.15s,
    background 0.2s;
}

button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0px);
}

.add-btn,
.submit-btn,
.remove-btn {
  border: none;
  border-radius: 12px;

  padding: 0.85rem 1.1rem;

  font-weight: 600;
  font-size: 0.95rem;
}

.submit-btn {
  background: var(--accent);
  color: white;

  min-width: 220px;

  box-shadow:
    0 4px 10px rgba(25, 195, 125, 0.25);
}

.submit-btn:hover {
  background: var(--accent-hover);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.add-btn {
  background: #e9eef2;
  color: var(--text);
}

.add-btn:hover {
  background: #dde5ea;
}

.remove-btn {
  background: #fff1f2;
  color: var(--danger);
}

.remove-btn:hover {
  background: #ffe4e6;
}

.success,
.error {
  margin-top: 1.4rem;

  padding: 1rem 1.2rem;

  border-radius: 12px;

  font-weight: 600;
}

.success {
  background: #ecfdf3;
  color: var(--success);
  border: 1px solid #bbf7d0;
}

.error {
  background: #fef2f2;
  color: var(--danger);
  border: 1px solid #fecaca;
}

hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}
</style>