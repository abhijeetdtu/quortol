<template>
  <div class="portfolio-list">
    <h1>Portfolio</h1>
    
    <div v-if="loading" class="loading">Loading projects...</div>
    <div v-else class="projects-container">
      <div v-if="projects.length === 0" class="no-projects">No projects yet.</div>
      <div v-else class="projects-grid">
        <div v-for="project in projects" :key="project.id" class="project-card">
          <h3>{{ project.title }}</h3>
          <p>{{ project.description }}</p>
          <div v-if="project.techstacks?.length" class="techstacks">
            <span v-for="tech in project.techstacks" :key="tech.id" class="tech-badge">{{ tech.name }}</span>
          </div>
          <router-link :to="`/portfolio/${project.slug}`" class="view-project">View Project →</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { portfolio } from '../../services/api'

const projects = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await portfolio.getProjects()
    projects.value = response.data
  } catch (error) {
    console.error('Error loading projects:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style>
.portfolio-list {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.portfolio-list h1 {
  margin-bottom: 2rem;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.project-card h3 {
  margin-bottom: 0.5rem;
}

.techstacks {
  margin: 1rem 0;
}

.tech-badge {
  background: #9b59b6;
  color: #fff;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-right: 0.5rem;
  display: inline-block;
}

.view-project {
  color: #9b59b6;
  text-decoration: none;
}

.view-project:hover {
  text-decoration: underline;
}

.loading, .no-projects {
  text-align: center;
  color: #666;
  padding: 2rem;
}
</style>