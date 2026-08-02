<template>
  <section class="context-section" aria-labelledby="context-heading">
    <div class="context-heading-row">
      <div>
        <p class="context-kicker">Document context</p>
        <h2 id="context-heading">Choose where to continue</h2>
      </div>
      <p id="context-instructions">Scroll through the text and select any word to continue from there.</p>
    </div>

    <div
      ref="viewport"
      class="context-viewport"
      tabindex="0"
      aria-describedby="context-instructions"
      @click="handleDocumentClick"
    ><span>{{ textBefore }}</span><button
        v-if="currentToken"
        ref="currentWord"
        type="button"
        class="context-word is-current"
        aria-current="true"
        :aria-label="`Current word ${safeCurrentIndex + 1}: ${currentToken.text}`"
        @click.stop="$emit('seek', safeCurrentIndex)"
      >{{ currentToken.text }}</button><span>{{ textAfter }}</span></div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  content: { type: String, required: true },
  currentIndex: { type: Number, default: 0 },
  active: { type: Boolean, default: true },
})

const emit = defineEmits(['seek'])
const viewport = ref(null)
const currentWord = ref(null)

const words = computed(() => {
  const matches = []
  const pattern = /\S+/g
  let match = pattern.exec(props.content)
  while (match) {
    matches.push({ text: match[0], start: match.index, end: pattern.lastIndex })
    match = pattern.exec(props.content)
  }
  return matches
})

const safeCurrentIndex = computed(() => Math.max(
  0,
  Math.min(words.value.length - 1, Math.trunc(props.currentIndex)),
))
const currentToken = computed(() => words.value[safeCurrentIndex.value] || null)
const textBefore = computed(() => currentToken.value ? props.content.slice(0, currentToken.value.start) : props.content)
const textAfter = computed(() => currentToken.value ? props.content.slice(currentToken.value.end) : '')

const prefersReducedMotion = () => (
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
)

const centerCurrentWord = async () => {
  await nextTick()
  if (!props.active || !currentWord.value) return
  currentWord.value.scrollIntoView?.({
    block: 'center',
    inline: 'nearest',
    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
  })
}

const globalTextOffset = (node, localOffset) => {
  if (!viewport.value || !node || !viewport.value.contains(node)) return null
  const range = document.createRange()
  range.setStart(viewport.value, 0)
  try {
    range.setEnd(node, localOffset)
  } catch {
    return null
  }
  return range.toString().length
}

const wordIndexAtOffset = (offset) => {
  let low = 0
  let high = words.value.length - 1
  while (low <= high) {
    const middle = Math.floor((low + high) / 2)
    const word = words.value[middle]
    if (offset < word.start) high = middle - 1
    else if (offset >= word.end) low = middle + 1
    else return middle
  }
  return Math.max(0, Math.min(words.value.length - 1, low))
}

const handleDocumentClick = (event) => {
  if (!words.value.length || typeof document === 'undefined') return
  let node = null
  let offset = 0
  if (typeof document.caretPositionFromPoint === 'function') {
    const position = document.caretPositionFromPoint(event.clientX, event.clientY)
    node = position?.offsetNode
    offset = position?.offset ?? 0
  } else if (typeof document.caretRangeFromPoint === 'function') {
    const range = document.caretRangeFromPoint(event.clientX, event.clientY)
    node = range?.startContainer
    offset = range?.startOffset ?? 0
  }
  const textOffset = globalTextOffset(node, offset)
  if (textOffset !== null) emit('seek', wordIndexAtOffset(textOffset))
}

watch(() => props.currentIndex, centerCurrentWord)
watch(() => props.active, (active) => {
  if (active) window.setTimeout(centerCurrentWord, 0)
})
watch(() => props.content, centerCurrentWord)
onMounted(centerCurrentWord)

defineExpose({ centerCurrentWord })
</script>

<style scoped>
.context-section { max-width: 70ch; margin: 0 auto 2.5rem; }
.context-heading-row { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: .75rem; }
.context-heading-row h2, .context-heading-row p { margin: 0; }
.context-heading-row > p { max-width: 35ch; color: var(--ink-soft); font-size: .85rem; }
.context-kicker { color: var(--accent); font-size: .74rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; }
.context-viewport {
  height: min(48vh, 520px);
  min-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 1.25rem;
  background: var(--surface-raised);
  color: rgba(26, 26, 26, .35);
  line-height: 1.9;
  white-space: pre-wrap;
  cursor: text;
}
.context-word {
  display: inline;
  margin: 0;
  border: 0;
  border-radius: 3px;
  padding: .05em .18em;
  background: #4a3d2b;
  color: #fff;
  font: inherit;
  font-weight: 600;
  line-height: inherit;
  cursor: pointer;
  box-shadow: 0 0 0 2px rgba(74, 61, 43, .18);
}
.context-word:focus-visible, .context-viewport:focus-visible { outline: 3px solid #f77f00; outline-offset: 2px; }
@media (max-width: 600px) { .context-heading-row { align-items: start; flex-direction: column; } }
@media (prefers-reduced-motion: reduce) { .context-viewport { scroll-behavior: auto; } }
</style>
