<template>
  <div class="portfolio-detail">
    <router-link to="/portfolio" class="back-link">← Back to Portfolio</router-link>
    
    <div v-if="loading" class="loading">Loading project...</div>
    <div v-else-if="project" class="project-content">
      <h1>{{ project.title }}</h1>
      <div class="meta">
        <span>Published: {{ formatDate(project.published_at) }}</span>
      </div>
      
      <div v-if="project.image_url" class="project-image">
        <img :src="project.image_url" :alt="project.title">
      </div>
      
      <div class="description">
        <h2>Description</h2>
        <p>{{ project.description }}</p>
      </div>
      
      <div v-if="project.long_description" class="long-description">
        <h2>Details</h2>
        <p>{{ project.long_description }}</p>
      </div>
      
      <div class="techstacks">
        <h2>Tech Stack</h2>
        <div v-if="project.techstacks?.length" class="tech-grid">
          <span v-for="tech in project.techstacks" :key="tech.id" class="tech-badge">
            {{ tech.name }}
          </span>
        </div>
      </div>
      
      <div class="links">
        <router-link v-if="project.live_url" :to="project.live_url" class="btn btn-live" target="_blank">
          View Live →
        </router-link>
        <a v-if="project.repo_url" :href="project.repo_url" class="btn btn-repo" target="_blank">
          View Repo →
        </a>
      </div>
    </div>
    <div v-else class="not-found">Project not found</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { portfolio } from '../../services/api'

const route = useRoute()
const project = ref(null)
const loading = ref(true)

const slug = computed(() => route.params.slug)

onMounted(async () => {
  try {
    const response = await portfolio.getProject(slug.value)
    project.value = response.data
  } catch (error) {
    console.error('Error loading project:', error)
  } finally {
    loading.value = false
  }
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style>
.portfolio-detail {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.back-link {
  display: block;
  margin-bottom: 1rem;
  color: #9b59b6;
  text-decoration: none;
}

.project-content h1 {
  margin-bottom: 1rem;
}

.meta {
  margin-bottom: 2rem;
  color: #666;
}

.project-image {
  margin: 2rem 0;
}

.project-image img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.description, .long-description, .techstacks {
  margin: 2rem 0;
}

.description h2, .long-description h2, .techstacks h2 {
  margin-bottom: 1rem;
}

.tech-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-badge {
  background: none;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  box-shadow: inset 0 0 0 1px rgba(155, 89, 182, 0.65);
}

.links {
  margin-top: 3rem;
}

.btn {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  border-radius: 5px;
  text-decoration: none;
  margin-right: 1rem;
  transition: all 0.3s;
}

.btn-live {
  background: none;
  color: #fff;
  box-shadow: inset 0 0 0 1px rgba(39, 174, 96, 0.68);
}

.btn-repo {
  background: none;
  color: #fff;
  box-shadow: inset 0 0 0 1px rgba(51, 51, 51, 0.68);
}

.loading, .not-found {
  text-align: center;
  padding: 2rem;
}

.not-found {
  color: #e74c3c;
}
</style>
