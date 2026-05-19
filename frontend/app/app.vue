<template>
  <div>
    <nav class="nav">
      <NuxtLink to="/">Register Device</NuxtLink>
      <NuxtLink to="/data">Data Browser</NuxtLink>
    </nav>

    <NuxtPage />
  </div>
</template>

<style>
body {
  margin: 0;
}

.nav {
  display: flex;
  gap: 1rem;

  padding: 1rem 2rem;

  background: #111827;
}

.nav a {
  color: white;
  text-decoration: none;
  font-weight: 600;
}

.nav a:hover {
  color: #19c37d;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  z-index: 1000;
}

.modal {
  width: min(900px, 100%);
  max-height: 80vh;
  overflow: auto;
  background: white;
  border-radius: 18px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal pre {
  background: #0f172a;
  color: #e5e7eb;
  padding: 1rem;
  border-radius: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
</style>