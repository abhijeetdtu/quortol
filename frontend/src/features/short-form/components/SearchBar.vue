<template>
  <div class="search-bar-container">
    <input
      ref="searchInput"
      type="text"
      v-model="keyword"
      placeholder="Search posts..."
      @input="handleSearch"
      :disabled="loading"
      class="search-input"
      aria-label="Search posts by keyword"
    />
    <button
      v-if="hasKeyword && !loading"
      @click="clearSearch"
      class="clear-button"
      aria-label="Clear search"
    >
      x
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'search'])

const keyword = ref(props.modelValue)
const debounceTimer = ref(null)
const searchInput = ref(null)
const DEBOUNCE_DELAY = 300

const hasKeyword = computed(() => keyword.value.trim().length > 0)

watch(
  () => props.modelValue,
  (value) => {
    if (value !== keyword.value) {
      keyword.value = value || ''
    }
  },
)

const emitSearch = (value) => {
  emit('update:modelValue', value)
  emit('search', value)
}

const handleSearch = () => {
  clearTimeout(debounceTimer.value)

  debounceTimer.value = setTimeout(() => {
    emitSearch(keyword.value.trim())
  }, DEBOUNCE_DELAY)
}

const clearSearch = () => {
  keyword.value = ''
  emitSearch('')
  searchInput.value?.focus()
}
</script>

<style scoped>
.search-bar-container {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 8px 36px 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  font-size: 14px;
  background-color: var(--bg-secondary, #f9f9f9);
  color: var(--text-primary, #333);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color, #4a90d9);
  background-color: var(--bg-white, #fff);
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.2);
}

.search-input:disabled {
  background-color: var(--bg-disabled, #e0e0e0);
  cursor: not-allowed;
}

.clear-button {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--text-muted, #999);
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.clear-button:hover {
  background-color: rgba(0, 0, 0, 0.1);
  color: var(--text-primary, #333);
}

@media (max-width: 768px) {
  .search-bar-container {
    max-width: 100%;
  }
}
</style>
