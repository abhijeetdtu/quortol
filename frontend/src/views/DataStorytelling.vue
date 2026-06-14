<template>
  <section class="container-xl py-4">
    <header class="mb-3">
      <p class="kicker mb-2">Data Storytelling</p>
      <h1 class="h2 mb-2">Interactive dashboards and visual deep dives</h1>
      <p class="intro mb-0">
        Explore Quortol dashboards in an embedded workspace built for exploratory analysis and longform visual explanation.
      </p>
    </header>
    <div class="card app-card">
      <div class="card-body p-0">
        <iframe
          :src="iframeSrc"
          title="Data Storytelling"
          class="dashboard-frame"
        ></iframe>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const iframeSrc = computed(() => {
  const dashboard = typeof route.params.dashboard === 'string'
    ? route.params.dashboard.trim()
    : ''
  return dashboard
    ? `/data-storytelling-app/${dashboard}`
    : '/data-storytelling-app/'
})
</script>

<style scoped>
.kicker {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.intro {
  color: var(--ink-muted);
  max-width: 68ch;
}

.app-card {
  background: none;
  border: none;
  border-radius: 4px;
  box-shadow: var(--soft-shadow);
}

.dashboard-frame {
  display: block;
  width: 100%;
  height: min(980px, calc(100dvh - 180px));
  min-height: 560px;
  border: none;
  border-radius: 4px;
  background: #fff;
}

@media (max-width: 992px) {
  .dashboard-frame {
    height: calc(100dvh - 160px);
    min-height: 520px;
  }
}

@media (max-width: 576px) {
  .dashboard-frame {
    height: calc(100dvh - 140px);
    min-height: 460px;
    border-radius: 0;
  }
}
</style>
