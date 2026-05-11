<script setup>
const { data, pending, error } = await useFetch(
  'http://127.0.0.1:8000/devices'
)
</script>

<template>
  <div style="padding: 2rem;">
    <h1>IoT Device Registry</h1>

    <div v-if="pending">
      Loading...
    </div>

    <div v-else-if="error">
      Error loading devices
    </div>

    <div v-else>
      <div
        v-for="device in data"
        :key="device.device_id"
        style="
          border: 1px solid #ccc;
          padding: 1rem;
          margin-bottom: 1rem;
          border-radius: 8px;
        "
      >
        <h3>{{ device.device_id }}</h3>

        <p>
          Type: {{ device.device_type }}
        </p>

        <p>
          Location: {{ device.location }}
        </p>
      </div>
    </div>
  </div>
</template>