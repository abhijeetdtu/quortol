<template>
  <div class="portfolio-list container-xl py-5">
    <header class="mb-4">
      <p class="kicker mb-2">Project Archive</p>
      <h1 class="display-6 mb-2">Portfolio</h1>
      <p class="intro mb-0">Selected builds, case studies, and implementation notes.</p>
    </header>

    <div v-if="loading" class="text-muted py-4">Loading projects...</div>
    <div v-else-if="projects.length === 0" class="text-muted py-4">No projects yet.</div>
    <div v-else class="row g-3">
      <div v-for="project in projects" :key="project.id" class="col-12 col-md-6 col-xl-4">
        <article class="card h-100 app-card">
          <div class="card-body">
            <h3 class="h4 card-title">{{ project.title }}</h3>
            <p class="card-text text-secondary">{{ project.description }}</p>
            <div v-if="project.techstacks?.length" class="d-flex flex-wrap gap-2 my-3">
              <span v-for="tech in project.techstacks" :key="tech.id" class="badge rounded-pill app-badge">
                {{ tech.name }}
              </span>
            </div>
            <router-link :to="`/portfolio/${project.slug}`" class="app-link">View project &rarr;</router-link>
          </div>
        </article>
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

<style scoped>
.kicker {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.intro {
  color: var(--ink-muted);
}

.app-card {
  background: none;
  border: none;
  border-radius: 4px;
  box-shadow: var(--soft-shadow);
}

.app-link {
  color: #7f3a27;
  text-decoration: none;
  font-weight: 600;
}

.app-link:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.app-badge {
  border: none;
  color: #594f40;
  background: none;
  box-shadow: inset 0 0 0 1px rgba(126, 107, 79, 0.24);
  font-weight: 500;
}
</style>
