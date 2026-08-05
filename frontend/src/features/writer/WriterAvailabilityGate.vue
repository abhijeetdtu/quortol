<template>
  <Writer v-if="availability === 'available'" />
  <section v-else class="writer-status-page container py-5" aria-live="polite">
    <div class="writer-status-card mx-auto p-4 p-md-5 text-center">
      <template v-if="availability === 'unknown'">
        <h1>Checking Writing Assistant</h1>
        <p class="mb-0">Confirming that the local writing model is available…</p>
      </template>
      <template v-else>
        <h1>Writing Assistant is currently unavailable</h1>
        <p class="mb-0">The local writing model could not be reached. Please try again later.</p>
      </template>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import Writer from '../../views/Writer.vue'
import { checkWriterAvailability, writerAvailability as availability } from './availability'

onMounted(() => {
  checkWriterAvailability({ force: true })
})
</script>

<style scoped>
.writer-status-page {
  min-height: 60vh;
  display: grid;
  place-items: center;
}

.writer-status-card {
  max-width: 42rem;
  color: var(--ink);
  background: var(--surface-raised);
  border: 1px solid var(--line);
  border-radius: 0.75rem;
  box-shadow: var(--soft-shadow);
}

.writer-status-card p {
  color: var(--ink-muted);
}
</style>
