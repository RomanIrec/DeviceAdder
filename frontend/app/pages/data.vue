<script setup>
const config = useRuntimeConfig()

const devices = ref([])
const selectedDevice = ref('')
const search = ref('')
const metrics = ref([])
const selectedMetric = ref('')
const startDate = ref('')
const endDate = ref('')
const rows = ref([])
const loading = ref(false)
const errorMessage = ref('')

const filteredDevices = computed(() => {
  return devices.value.filter(device =>
    device.device_id.toLowerCase().includes(search.value.toLowerCase())
  )
})

const pivotedRows = computed(() => {
  const grouped = {}

  for (const row of rows.value) {
    const key = `${row.measurement_date}_${row.device_id}`

    if (!grouped[key]) {
      grouped[key] = {
        measurement_date: row.measurement_date,
        device_id: row.device_id,
      }
    }

    const columnName = `${row.metric_name} [${row.metric_unit || ''}]`
    grouped[key][columnName] = row.metric_value
  }

  return Object.values(grouped)
})

const pivotColumns = computed(() => {
  const columns = new Set()

  for (const row of rows.value) {
    columns.add(`${row.metric_name} [${row.metric_unit || ''}]`)
  }

  return Array.from(columns)
})

async function loadDevices() {
  devices.value = await $fetch(`${config.public.apiBase}/devices`)
}

async function loadMetrics() {
  selectedMetric.value = ''
  rows.value = []

  if (!selectedDevice.value) return

  metrics.value = await $fetch(
    `${config.public.apiBase}/devices/${selectedDevice.value}/metrics`
  )
}

async function loadMeasurements() {
  if (!selectedDevice.value) return

  loading.value = true
  errorMessage.value = ''

  try {
    const query = {}

    if (selectedMetric.value) query.metric_name = selectedMetric.value
    if (startDate.value) query.start_date = startDate.value
    if (endDate.value) query.end_date = endDate.value

    rows.value = await $fetch(
      `${config.public.apiBase}/devices/${selectedDevice.value}/measurements`,
      { query }
    )
  } catch (err) {
    errorMessage.value = 'Failed to load measurements'
  } finally {
    loading.value = false
  }
}

onMounted(loadDevices)
</script>

<template>
  <div class="container">
    <h1>Device Data Browser</h1>

    <p class="subtitle">
      View measurements stored in PostgreSQL without writing SQL queries.
    </p>

    <div class="panel">
      <div class="field">
        <label>Search device</label>
        <input v-model="search" placeholder="Type device_id..." />
      </div>

      <div class="field">
        <label>Select device</label>
        <select v-model="selectedDevice" @change="loadMetrics">
          <option value="">Select device...</option>
          <option
            v-for="device in filteredDevices"
            :key="device.device_id"
            :value="device.device_id"
          >
            {{ device.device_id }} — {{ device.pipeline }}
          </option>
        </select>
      </div>

      <div class="field">
        <label>Metric</label>
        <select v-model="selectedMetric">
          <option value="">All metrics</option>
          <option
            v-for="metric in metrics"
            :key="metric"
            :value="metric"
          >
            {{ metric }}
          </option>
        </select>
      </div>

      <div class="field">
        <label>Start date</label>
        <input v-model="startDate" type="datetime-local" />
      </div>

      <div class="field">
        <label>End date</label>
        <input v-model="endDate" type="datetime-local" />
      </div>

      <button class="submit-btn" @click="loadMeasurements">
        Load data
      </button>
    </div>

    <div v-if="errorMessage" class="error">
      {{ errorMessage }}
    </div>

    <div v-if="loading" class="subtitle">
      Loading...
    </div>

    <table v-if="pivotedRows.length" class="data-table">
        <thead>
            <tr>
            <th>Date</th>
            <th>Device</th>

            <th
                v-for="column in pivotColumns"
                :key="column"
            >
                {{ column }}
            </th>
            </tr>
        </thead>

        <tbody>
            <tr
            v-for="row in pivotedRows"
            :key="row.measurement_date + row.device_id"
            >
            <td>{{ row.measurement_date }}</td>
            <td>{{ row.device_id }}</td>

            <td
                v-for="column in pivotColumns"
                :key="column"
            >
                {{ row[column] ?? '-' }}
            </td>
            </tr>
        </tbody>
    </table>
  </div>
</template>

