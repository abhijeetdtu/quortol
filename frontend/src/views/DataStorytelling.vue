<template>
  <section class="container-xl py-4">
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
