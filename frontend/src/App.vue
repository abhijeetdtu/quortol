<template>
  <div id="app">
    <Navbar v-if="!hideShell" />
    <main>
      <router-view />
    </main>
    <Footer v-if="!hideShell" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth.js'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'

const authStore = useAuthStore()
const route = useRoute()
const hideShell = computed(() => Boolean(route.meta?.hideShell))

onMounted(() => {
  authStore.checkAuth()
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:wght@400;500;600&display=swap');

:root {
  --page-bg: #fbfaf7;
  --surface: #f5f2ec;
  --ink: #1a1a1a;
  --ink-muted: #5f5a4f;
  --ink-soft: #7d776a;
  --line: #dad2c4;
  --accent: #8a3c2a;
  --display-font: 'Fraunces', Georgia, 'Times New Roman', serif;
  --body-font: 'Source Sans 3', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  font-family: var(--body-font);
  line-height: 1.6;
  color: var(--ink);
  background-color: var(--page-bg);
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: var(--display-font);
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.01em;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style>
