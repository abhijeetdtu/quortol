<template>
  <div class="tag-filter-container" ref="containerRef">
    <label class="tag-label" for="tag-filter">Filter by tags:</label>

    <div class="selected-tags" v-if="selectedTags.length > 0">
      <span
        v-for="tag in selectedTags"
        :key="tag"
        class="tag-pill"
        @click="removeTag(tag)"
        tabindex="0"
        role="button"
      >
        {{ tag }}
        <span class="remove-icon">x</span>
      </span>
    </div>

    <div class="dropdown-container">
      <input
        id="tag-filter"
        ref="searchInput"
        type="text"
        v-model="filterText"
        placeholder="Select tags..."
        @focus="openDropdown"
        @input="handleFilterText"
        @keydown.down.prevent="navigateOptions(1)"
        @keydown.up.prevent="navigateOptions(-1)"
        @keydown.enter.prevent="selectCurrentOption"
        @keydown.esc.prevent="closeDropdown"
        class="filter-input"
        :aria-expanded="isOpen"
        :aria-controls="`tag-options-${id}`"
      />

      <div v-show="isOpen" class="dropdown-menu" :id="`tag-options-${id}`">
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          class="dropdown-option"
          :class="{ selected: isSelected(option.value), active: index === currentIndex }"
          tabindex="-1"
          @click="toggleSelected(option.value)"
          @mouseenter="currentIndex = index"
        >
          <span class="tag-checkbox">
            <input type="checkbox" :checked="isSelected(option.value)" readonly />
          </span>
          <span class="tag-label-display">{{ option.label }}</span>
        </div>

        <div v-if="filteredOptions.length === 0" class="no-results">No matching tags found</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  availableTags: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedTags = ref([...props.modelValue])
const filterText = ref('')
const isOpen = ref(false)
const currentIndex = ref(-1)
const id = `tag-filter-${Math.random().toString(36).slice(2, 9)}`
const containerRef = ref(null)

watch(
  () => props.modelValue,
  (newVal) => {
    selectedTags.value = [...(newVal || [])]
  },
)

const filteredOptions = computed(() => {
  const searchTerm = filterText.value.toLowerCase().trim()

  return (props.availableTags || [])
    .map((tag) => ({ value: tag, label: tag }))
    .filter((option) => !searchTerm || option.label.toLowerCase().includes(searchTerm))
})

const isSelected = (tag) => selectedTags.value.includes(tag)

const syncSelection = () => {
  const next = [...selectedTags.value]
  emit('update:modelValue', next)
  emit('change', next)
}

const toggleSelected = (tag) => {
  const idx = selectedTags.value.indexOf(tag)
  if (idx >= 0) {
    selectedTags.value.splice(idx, 1)
  } else {
    selectedTags.value.push(tag)
  }

  syncSelection()
}

const removeTag = (tag) => {
  const idx = selectedTags.value.indexOf(tag)
  if (idx >= 0) {
    selectedTags.value.splice(idx, 1)
    syncSelection()
  }
}

const openDropdown = () => {
  isOpen.value = true
}

const closeDropdown = () => {
  isOpen.value = false
  filterText.value = ''
  currentIndex.value = -1
}

const handleFilterText = () => {
  isOpen.value = true
  currentIndex.value = filteredOptions.value.length > 0 ? 0 : -1
}

const navigateOptions = (direction) => {
  if (filteredOptions.value.length === 0) return

  const next = currentIndex.value + direction
  if (next < 0) {
    currentIndex.value = filteredOptions.value.length - 1
  } else if (next >= filteredOptions.value.length) {
    currentIndex.value = 0
  } else {
    currentIndex.value = next
  }
}

const selectCurrentOption = () => {
  if (currentIndex.value < 0 || currentIndex.value >= filteredOptions.value.length) return
  toggleSelected(filteredOptions.value[currentIndex.value].value)
}

const handleDocumentClick = (event) => {
  if (!containerRef.value) return
  if (!containerRef.value.contains(event.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
.tag-filter-container {
  margin-bottom: 16px;
}

.tag-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
  margin-bottom: 8px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background-color: var(--accent-light, #e8f4fc);
  border-radius: 16px;
  font-size: 13px;
  color: var(--text-primary, #333);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-pill:hover {
  background-color: var(--accent-color, #4a90d9);
  color: white;
}

.tag-pill .remove-icon {
  margin-left: 6px;
  font-weight: bold;
  opacity: 0.7;
}

.dropdown-container {
  position: relative;
  width: 100%;
}

.filter-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  font-size: 14px;
  background-color: var(--bg-secondary, #f9f9f9);
  color: var(--text-primary, #333);
  transition: all 0.2s ease;
}

.filter-input:focus {
  outline: none;
  border-color: var(--accent-color, #4a90d9);
  background-color: var(--bg-white, #fff);
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.2);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background-color: var(--bg-white, #fff);
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.dropdown-option:hover,
.dropdown-option.active {
  background-color: var(--bg-hover, #f5f5f5);
}

.dropdown-option.selected {
  background-color: var(--accent-light, #e8f4fc);
}

.tag-checkbox {
  margin-right: 8px;
}

.tag-checkbox input[type='checkbox'] {
  margin: 0;
}

.tag-label-display {
  font-size: 14px;
  color: var(--text-primary, #333);
}

.no-results {
  padding: 12px;
  text-align: center;
  color: var(--text-muted, #999);
  font-size: 13px;
}

@media (max-width: 768px) {
  .selected-tags {
    max-height: 150px;
    overflow-y: auto;
  }
}
</style>
