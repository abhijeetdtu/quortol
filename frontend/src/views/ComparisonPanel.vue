<template>
  <div class="comparison-panel">
    <!-- Comparison Mode Selector -->
    <div class="comparison-controls">
      <h3>Comparison Mode</h3>
      <label>
        <input type="checkbox" v-model="comparisonMode" />
        Enable Comparison
      </label>
    </div>

    <!-- Metric Selectors -->
    <div class="metric-selectors" v-if="comparisonMode">
      <div class="metric-selector" v-for="(metric, index) in selectedMetrics" :key="index">
        <label>
          Metric {{ index + 1 }}:
          <select v-model="metric.name" @change="updateMetrics">
            <option value="" disabled>Select metric</option>
            <option v-for="opt in availableMetrics" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </label>
        <button @click="removeMetric(index)" class="remove-btn">×</button>
      </div>

      <button @click="addMetric" class="add-btn">
        + Add Metric
      </button>

      <!-- Comparison Legend -->
      <div class="comparison-legend" v-if="selectedMetrics.length > 1">
        <h4>Selected Metrics:</h4>
        <ul>
          <li v-for="metric in selectedMetrics" :key="metric.name">
            {{ metric.label }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Export Button -->
    <div class="export-controls">
      <button @click="exportChart" class="export-btn">
        Export Chart
      </button>
      <button @click="exportData" class="export-btn">
        Export Data
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComparisonPanel',
  props: {
    availableMetrics: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      comparisonMode: false,
      selectedMetrics: [],
      exportFormats: ['PNG', 'PDF', 'CSV']
    }
  },
  methods: {
    addMetric() {
      if (this.selectedMetrics.length < 5) {
        this.selectedMetrics.push({
          value: '',
          label: ''
        })
      }
    },
    removeMetric(index) {
      this.selectedMetrics.splice(index, 1)
    },
    updateMetrics() {
      // Trigger parent component to update chart
      this.$emit('metrics-updated', this.selectedMetrics)
    },
    exportChart(format = 'PNG') {
      // Trigger parent component to export
      this.$emit('export-chart', { format })
    },
    exportData(format = 'CSV') {
      // Trigger parent component to export data
      this.$emit('export-data', { format })
    }
  }
}
</script>

<style scoped>
.comparison-panel {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.comparison-controls {
  margin-bottom: 1rem;
}

.metric-selectors {
  margin-top: 1rem;
}

.metric-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.remove-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2rem;
}

.add-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.export-controls {
  margin-top: 1rem;
}

.export-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.comparison-legend {
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
}

.comparison-legend ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
</style>
