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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #fff;
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
