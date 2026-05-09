<template>
  <div class="home-page container-xl py-5">
    <section class="hero mb-5">
      <p class="kicker mb-2">Curated</p>
      <h1 class="display-5 mb-3">Come satisfy your curiosity</h1>
      <p class="intro mb-4">
        Browse longform writing, review portfolio builds, or jump into agent tooling with one coherent editorial UI.
      </p>
      <div class="d-flex flex-wrap gap-2">
        <router-link to="/" class="btn btn-sm app-btn-accent">Open Explorer</router-link>
        <router-link to="/blog" class="btn btn-sm app-btn-soft">Read Blog</router-link>
        <router-link to="/portfolio" class="btn btn-sm app-btn-soft">View Portfolio</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/agent/login" class="btn btn-sm app-btn-soft">
          Access Agents
        </router-link>
        <router-link v-else to="/agent/dashboard" class="btn btn-sm app-btn-soft">Agent Dashboard</router-link>
      </div>
    </section>

    <section class="mb-5">
      <h2 class="mb-3">Latest Essays</h2>
      <div v-if="posts.length === 0" class="text-muted">Loading...</div>
      <div v-else class="row g-3">
        <div v-for="post in posts.slice(0, 3)" :key="post.id" class="col-12 col-md-6 col-xl-4">
          <article class="card h-100 app-card">
            <div class="card-body">
              <h3 class="h4 card-title">{{ post.title }}</h3>
              <p class="card-text text-secondary">{{ post.excerpt }}</p>
              <router-link :to="`/blog/${post.slug}`" class="app-link">Read Essay &rarr;</router-link>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section>
      <h2 class="mb-3">Featured Projects</h2>
      <div v-if="projects.length === 0" class="text-muted">Loading...</div>
      <div v-else class="row g-3">
        <div v-for="project in projects.slice(0, 3)" :key="project.id" class="col-12 col-md-6 col-xl-4">
          <article class="card h-100 app-card">
            <div class="card-body">
              <h3 class="h4 card-title">{{ project.title }}</h3>
              <p class="card-text text-secondary">{{ project.description }}</p>
              <router-link :to="`/portfolio/${project.slug}`" class="app-link">View Project &rarr;</router-link>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { blog, portfolio } from '../services/api'

const authStore = useAuthStore()
const posts = ref([])
const projects = ref([])

onMounted(async () => {
  try {
    const [postsRes, projectsRes] = await Promise.all([blog.getPosts(), portfolio.getProjects()])
    posts.value = postsRes.data
    projects.value = projectsRes.data
  } catch (error) {
    console.error('Error loading home data:', error)
  }
})
</script>

<style scoped>
.hero {
  max-width: 72ch;
}

.kicker {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.intro {
  color: var(--ink-muted);
  font-size: 1.08rem;
  line-height: 1.55;
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

.app-btn-soft {
  background: none;
  border: none;
  color: #4e4438;
  box-shadow: inset 0 0 0 1px rgba(146, 126, 95, 0.18);
}

.app-btn-soft:hover {
  background: none;
  color: #4e4438;
  box-shadow: inset 0 0 0 1px rgba(146, 126, 95, 0.36);
}

.app-btn-accent {
  border: none;
  background: none;
  color: #4a3314;
  box-shadow: inset 0 0 0 1px rgba(184, 132, 46, 0.35);
}

.app-btn-accent:hover {
  background: none;
  color: #4a3314;
  box-shadow: inset 0 0 0 1px rgba(184, 132, 46, 0.55);
}
</style>
