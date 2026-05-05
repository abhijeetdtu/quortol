<template>
  <div class="agent-dashboard">
    <h1>Agent Dashboard</h1>
    
    <div v-if="loading" class="loading">Loading agents...</div>
    <div v-else class="dashboard-content">
      <div v-if="agentList.length === 0" class="no-agents">No agents available yet.</div>
      <div v-else class="agents-grid">
        <div v-for="agent in agentList" :key="agent.id" class="agent-card">
          <h3>{{ agent.name }}</h3>
          <p class="description">{{ agent.description }}</p>
          <div class="status">
            <span :class="['status-badge', agent.status]">
              {{ agent.status.toUpperCase() }}
            </span>
          </div>
          <router-link 
            :to="`/agent/agents/${agent.id}/capabilities`" 
            class="view-capabilities"
          >
            View Capabilities →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agents } from '../../services/api'
import { useAuthStore } from '../../stores/auth.js'

const authStore = useAuthStore()
const agentList = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await agents.getAgents()
    agentList.value = response.data
  } catch (error) {
    console.error('Error loading agents:', error)
    authStore.logout()
  } finally {
    loading.value = false
  }
})
</script>

<style>
.agent-dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.agent-dashboard h1 {
  margin-bottom: 2rem;
}

.dashboard-content {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 2rem;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.agent-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.agent-card h3 {
  margin-bottom: 0.5rem;
}

.description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.status {
  margin: 1rem 0;
}

.status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: #27ae60;
  color: #fff;
}

.status-badge.inactive {
  background: #95a5a6;
  color: #fff;
}

.status-badge.maintenance {
  background: #f39c12;
  color: #fff;
}

.view-capabilities {
  color: #667eea;
  text-decoration: none;
}

.view-capabilities:hover {
  text-decoration: underline;
}

.loading, .no-agents {
  text-align: center;
  padding: 2rem;
}

.no-agents {
  color: #666;
}
</style>