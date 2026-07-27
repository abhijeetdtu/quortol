<template>
  <section class="container-xl py-4">
    <router-link to="/data-storytelling" class="back-link">&larr; Data Storytelling</router-link>
    <div v-if="loading" class="text-center text-muted py-5">Loading dashboard...</div>
    <div v-else-if="error" class="text-center py-5" role="alert">
      <h1 class="h3">Dashboard unavailable</h1><p class="text-muted">{{ error }}</p>
    </div>
    <div v-else-if="!dashboard" class="text-center py-5">
      <h1 class="h3">Dashboard not found</h1><p class="text-muted">This dashboard is not registered or is no longer public.</p>
    </div>
    <template v-else>
      <header class="my-3">
        <p class="kicker mb-2">Interactive dashboard</p>
        <h1 class="h2 mb-2">{{ dashboard.title }}</h1>
        <p class="intro mb-0">{{ dashboard.description }}</p>
      </header>
      <div class="dashboard-shell">
        <iframe :src="dashboard.embed_path" :title="dashboard.title" class="dashboard-frame"></iframe>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { dataStorytelling } from '../services/api'

const route = useRoute()
const dashboards = ref([])
const loading = ref(true)
const error = ref('')
const dashboard = computed(() => dashboards.value.find((item) => item.slug === route.params.dashboard) || null)
onMounted(async () => {
  try {
    const response = await dataStorytelling.getDashboards()
    dashboards.value = Array.isArray(response.data?.dashboards) ? response.data.dashboards : []
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'Please try again in a moment.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.back-link { color: #7f3a27; text-decoration: none; font-weight: 600; }
.back-link:hover { text-decoration: underline; text-underline-offset: 3px; }
.kicker { text-transform: uppercase; letter-spacing: .1em; font-size: .75rem; color: var(--ink-soft); }
.intro { color: var(--ink-muted); max-width: 68ch; }
.dashboard-shell { border-radius: 4px; box-shadow: var(--soft-shadow); overflow: hidden; }
.dashboard-frame { display: block; width: 100%; height: min(980px, calc(100dvh - 210px)); min-height: 560px; border: 0; background: #fff; }
@media (max-width: 576px) { .dashboard-frame { height: calc(100dvh - 170px); min-height: 460px; } }
</style>
