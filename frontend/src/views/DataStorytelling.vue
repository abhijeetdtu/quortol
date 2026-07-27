<template>
  <div class="story-index container-xl py-4 py-md-5">
    <header class="masthead mb-4">
      <p class="brand mb-2">Interactive</p>
      <h1 class="display-4 mb-2">Data Storytelling</h1>
      <p class="deck mb-0">Explore visual deep dives, simulations, and interactive data stories.</p>
    </header>

    <div v-if="loading" class="text-center text-muted py-5">Loading dashboards...</div>
    <div v-else-if="error" class="py-5 text-center" role="alert">
      <h2 class="h4">Dashboards are temporarily unavailable</h2>
      <p class="text-muted mb-3">{{ error }}</p>
      <button class="btn retry-button" type="button" @click="loadDashboards">Try again</button>
    </div>
    <div v-else-if="dashboards.length === 0" class="text-center text-muted py-5">No dashboards are available yet.</div>

    <div v-else class="index-content">
      <article class="featured row g-3 g-lg-4 pb-4 mb-4">
        <div class="col-12 col-lg-7">
          <div class="dashboard-art dashboard-art--featured" :style="artStyle(0)" aria-hidden="true"></div>
        </div>
        <div class="col-12 col-lg-5">
          <div class="featured-copy h-100 d-flex flex-column">
            <p class="type mb-2">Featured dashboard</p>
            <h2 class="mb-2">{{ featuredDashboard.title }}</h2>
            <p class="description mb-3">{{ featuredDashboard.description }}</p>
            <router-link :to="featuredDashboard.public_path" class="explore-link mt-auto">Explore dashboard</router-link>
          </div>
        </div>
      </article>

      <section v-if="remainingDashboards.length" class="latest">
        <h3 class="mb-2">Latest</h3>
        <article v-for="(dashboard, index) in remainingDashboards" :key="dashboard.slug" class="story-row row g-3 py-3">
          <div class="col-12 col-md-4 col-lg-3">
            <div class="dashboard-art" :style="artStyle(index + 1)" aria-hidden="true"></div>
          </div>
          <div class="col-12 col-md-8 col-lg-9">
            <p class="type mb-1">Interactive story</p>
            <h4 class="mb-2">{{ dashboard.title }}</h4>
            <p class="description mb-2">{{ dashboard.description }}</p>
            <router-link :to="dashboard.public_path" class="explore-link">Explore dashboard</router-link>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePrerenderRouteData } from '../prerender/context'
import { dataStorytelling } from '../services/api'

const prerenderRouteData = usePrerenderRouteData()
const initialDashboards = Array.isArray(prerenderRouteData.value?.dashboards) ? prerenderRouteData.value.dashboards : []
const dashboards = ref(initialDashboards)
const loading = ref(initialDashboards.length === 0)
const error = ref('')
const featuredDashboard = computed(() => dashboards.value[0] || null)
const remainingDashboards = computed(() => dashboards.value.slice(1))
const palettes = [['#003049', '#d62828', '#f77f00'], ['#1d3557', '#457b9d', '#a8dadc'], ['#432818', '#99582a', '#ffe6a7'], ['#264653', '#2a9d8f', '#e9c46a']]
const artStyle = (index) => {
  const colors = palettes[index % palettes.length]
  return { background: `radial-gradient(circle at 20% 20%, rgba(255,255,255,.3), transparent 42%), linear-gradient(142deg, ${colors[0]} 0%, ${colors[1]} 55%, ${colors[2]} 100%)` }
}
const loadDashboards = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await dataStorytelling.getDashboards()
    dashboards.value = Array.isArray(response.data?.dashboards) ? response.data.dashboards : []
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'Please try again in a moment.'
  } finally {
    loading.value = false
  }
}
onMounted(async () => {
  if (dashboards.value.length === 0) await loadDashboards()
})
</script>

<style scoped>
.brand, .type { text-transform: uppercase; letter-spacing: .1em; font-size: .75rem; color: var(--ink-soft); }
.deck, .description { color: var(--ink-muted); }
.deck { max-width: 68ch; font-size: 1.05rem; }
.featured-copy h2 { font-size: clamp(1.6rem, 2.8vw, 2.8rem); line-height: 1.1; }
.dashboard-art { width: 100%; height: 100%; min-height: 160px; border-radius: 2px; box-shadow: inset 0 0 0 1px rgba(133,121,99,.28), 0 8px 18px rgba(54,47,36,.08); }
.dashboard-art--featured { min-height: 300px; }
.story-row { border-radius: 8px; margin-bottom: .5rem; padding-inline: .35rem; box-shadow: var(--soft-shadow); }
.story-row h4 { font-size: 1.35rem; line-height: 1.18; }
.explore-link { color: #7f3a27; text-decoration: none; font-weight: 600; }
.explore-link:hover { text-decoration: underline; text-underline-offset: 3px; }
.retry-button { color: #6a3627; box-shadow: inset 0 0 0 1px rgba(106,54,39,.48); }
</style>
