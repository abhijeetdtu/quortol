<template>
  <aside class="analysis-panel" aria-labelledby="analysis-heading">
    <div class="analysis-topline">
      <p class="eyebrow">Editorial analysis</p>
      <span v-if="stale" class="stale" role="status">Analysis of an earlier draft</span>
    </div>
    <h2 id="analysis-heading">Whole-draft analysis</h2>

    <article v-for="block in blocks" :key="block.id" class="analysis-block" :data-block-id="block.id">
      <h3>{{ block.title }}</h3>
      <p>{{ block.content }}</p>
    </article>

    <div v-if="failedIds.length" class="partial-error" role="status">
      Some sections could not be completed: {{ failedIds.join(', ').replaceAll('_', ' ') }}.
    </div>
  </aside>
</template>

<script setup>
defineProps({
  blocks: { type: Array, default: () => [] },
  failedIds: { type: Array, default: () => [] },
  stale: { type: Boolean, default: false },
})
</script>

<style scoped>
.analysis-panel { background: var(--surface-raised); border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--soft-shadow); margin-top: 1.5rem; padding: 1.5rem; }
.analysis-topline { align-items: center; display: flex; justify-content: space-between; gap: 1rem; }
.eyebrow { color: var(--accent); font-size: .75rem; font-weight: 700; letter-spacing: .08em; margin: 0; text-transform: uppercase; }
.stale { background: #fff1cf; border-radius: 999px; color: #72500b; font-size: .8rem; padding: .3rem .6rem; }
h2 { margin: .4rem 0; } h3 { margin: 0 0 .45rem; }
.analysis-block { border-top: 1px solid var(--line); margin-top: 1.1rem; padding-top: 1.1rem; }
.analysis-block p { color: var(--ink); line-height: 1.65; margin: 0; white-space: pre-wrap; }
.partial-error { background: #fbe9e5; border-radius: 7px; color: #8b2f20; margin-top: 1rem; padding: .75rem; }
</style>
