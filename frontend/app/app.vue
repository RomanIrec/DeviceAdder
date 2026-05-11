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
    const response = await $fetch(
      'http://127.0.0.1:8000/devices',
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
body {
  font-family: Arial, sans-serif;
  background: #f5f5f5;
}

.container {
  max-width: 900px;
  margin: auto;
  padding: 2rem;
}

.field {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: bold;
}

input,
textarea,
select {
  width: 100%;
  padding: 0.7rem;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.metric-card {
  background: white;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
}

button {
  cursor: pointer;
}

.add-btn,
.submit-btn,
.remove-btn {
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 8px;
}

.add-btn {
  margin-bottom: 1rem;
}

.submit-btn {
  font-size: 1rem;
}

.success {
  margin-top: 1rem;
  color: green;
}

.error {
  margin-top: 1rem;
  color: red;
}
</style>