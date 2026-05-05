<template>
  <div class="agent-capabilities">
    <router-link to="/agent/dashboard" class="back-link">← Back to Agents</router-link>
    
    <div v-if="loading" class="loading">Loading agent...</div>
    <div v-else-if="agent" class="capability-content">
      <h1>{{ agent.name }}</h1>
      <div class="meta">
        <span>{{ agent.description }}</span>
        <span :class="['status', agent.status]">{{ agent.status.toUpperCase() }}</span>
      </div>
      
      <div v-if="agent.capabilities?.length" class="capabilities-section">
        <h2>Available Capabilities</h2>
        <div class="capabilities-list">
          <div v-for="cap in agent.capabilities" :key="cap" class="capability-item">
            <span class="capability-name">{{ cap }}</span>
          </div>
        </div>
      </div>
      
      <div class="execute-section">
        <h2>Execute Capability</h2>
        <form @submit.prevent="executeCapability" class="execute-form">
          <div class="form-group">
            <label for="capability">Select Capability</label>
            <select v-model="selectedCapability" required>
              <option value="">-- Choose a capability --</option>
              <option 
                v-for="cap in agent.capabilities" 
                :key="cap" 
                :value="cap"
              >
                {{ cap }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="params">Parameters (JSON)</label>
            <textarea 
              id="params" 
              v-model="paramsInput" 
              placeholder='{"param1": "value1", "param2": "value2"}'
              rows="4"
            ></textarea>
          </div>
          
          <div v-if="error" class="error">{{ error }}</div>
          <div v-if="successMessage" class="success">{{ successMessage }}</div>
          <div v-if="response" class="response-preview">
            <h3>Response</h3>
            <pre>{{ response }}</pre>
          </div>
          
          <button type="submit" class="submit-btn" :disabled="executing || !selectedCapability">
            <span v-if="executing">Executing...</span>
            <span v-else>Execute</span>
          </button>
        </form>
      </div>
    </div>
    <div v-else class="not-found">Agent not found</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { agents } from '../../services/api'

const route = useRoute()
const agent = ref(null)
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const response = ref(null)

const selectedCapability = ref('')
const paramsInput = ref('')
const executing = ref(false)

const agentId = computed(() => route.params.agentId)

onMounted(async () => {
  try {
    const response = await agents.getAgent(agentId.value)
    agent.value = response.data
  } catch (err) {
    console.error('Error loading agent:', err)
  } finally {
    loading.value = false
  }
})

const executeCapability = async () => {
  executing.value = true
  error.value = ''
  response.value = null
  
  let params
  try {
    params = paramsInput.value ? JSON.parse(paramsInput.value) : {}
  } catch (err) {
    error.value = 'Invalid JSON format for parameters'
    executing.value = false
    return
  }
  
  try {
    const result = await agents.execute(agentId.value, selectedCapability.value, params)
    response.value = JSON.stringify(result.data, null, 2)
    successMessage.value = 'Execution successful!'
  } catch (err) {
    error.value = err.response?.data?.error || 'Execution failed'
  } finally {
    executing.value = false
  }
}
</script>

<style>
.agent-capabilities {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.back-link {
  display: block;
  margin-bottom: 1rem;
  color: #667eea;
  text-decoration: none;
}

.capability-content h1 {
  margin-bottom: 0.5rem;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 2rem;
  color: #666;
}

.meta .status {
  font-weight: 500;
  text-transform: uppercase;
}

.meta .status.active {
  color: #27ae60;
}

.meta .status.inactive {
  color: #95a5a6;
}

.capabilities-section, .execute-section {
  margin: 2rem 0;
}

.capabilities-section h2, .execute-section h2 {
  margin-bottom: 1rem;
}

.capabilities-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.capability-item {
  background: #f8f9fa;
  padding: 0.8rem;
  border-radius: 5px;
}

.capability-name {
  font-family: monospace;
  color: #667eea;
}

.execute-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
}

.form-group select, .form-group textarea {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  font-family: inherit;
}

.form-group select:focus, .form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.error {
  color: #e74c3c;
  font-size: 0.9rem;
}

.success {
  color: #27ae60;
  font-size: 0.9rem;
}

.response-preview {
  background: #1e2a31;
  color: #a9fffe;
  padding: 1rem;
  border-radius: 5px;
  overflow-x: auto;
}

.response-preview pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.submit-btn {
  background: #667eea;
  color: #fff;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.3s;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading, .not-found {
  text-align: center;
  padding: 2rem;
}

.not-found {
  color: #e74c3c;
}
</style>