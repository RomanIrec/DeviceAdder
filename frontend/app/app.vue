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
</style>