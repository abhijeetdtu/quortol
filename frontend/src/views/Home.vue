<template>
  <div class="home">
    <section class="hero">
      <h1>Quortol Home</h1>
      <p>Blog, Portfolio, and Agent Access Platform</p>
      <div class="hero-actions">
        <router-link to="/" class="btn btn-pokhi">Open Pokhi Landing</router-link>
        <router-link to="/blog" class="btn btn-primary">Read Blog</router-link>
        <router-link to="/portfolio" class="btn btn-secondary">View Portfolio</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/agent/login" class="btn btn-agent">Access Agents</router-link>
        <router-link v-else to="/agent/dashboard" class="btn btn-agent">Agent Dashboard</router-link>
      </div>
    </section>

    <section class="latest-posts">
      <h2>Latest Blog Posts</h2>
      <div v-if="posts.length === 0" class="loading">Loading...</div>
      <div v-else class="posts-grid">
        <div v-for="post in posts.slice(0, 3)" :key="post.id" class="post-card">
          <h3>{{ post.title }}</h3>
          <p>{{ post.excerpt }}</p>
          <router-link :to="`/blog/${post.slug}`" class="read-more">Read More →</router-link>
        </div>
      </div>
    </section>

    <section class="latest-projects">
      <h2>Featured Projects</h2>
      <div v-if="projects.length === 0" class="loading">Loading...</div>
      <div v-else class="projects-grid">
        <div v-for="project in projects.slice(0, 3)" :key="project.id" class="project-card">
          <h3>{{ project.title }}</h3>
          <p>{{ project.description }}</p>
          <router-link :to="`/portfolio/${project.slug}`" class="view-project">View Project →</router-link>
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
    const [postsRes, projectsRes] = await Promise.all([
      blog.getPosts(),
      portfolio.getProjects()
    ])
    posts.value = postsRes.data
    projects.value = projectsRes.data
  } catch (error) {
    console.error('Error loading home data:', error)
  }
})
</script>

<style>
.home {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 4rem 0;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.8rem 1.5rem;
  border-radius: 5px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: #fff;
}

.btn-pokhi {
  background-color: #f39c12;
  color: #1f2d3d;
}

.btn-secondary {
  background-color: #9b59b6;
  color: #fff;
}

.btn-agent {
  background-color: #2c3e50;
  color: #fff;
}

.latest-posts, .latest-projects {
  margin: 3rem 0;
}

.latest-posts h2, .latest-projects h2 {
  margin-bottom: 1.5rem;
}

.posts-grid, .projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.post-card, .project-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.post-card h3, .project-card h3 {
  margin-bottom: 0.5rem;
}

.read-more, .view-project {
  color: #3498db;
  text-decoration: none;
  margin-top: 1rem;
  display: inline-block;
}

.read-more:hover, .view-project:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  color: #666;
}
</style>
