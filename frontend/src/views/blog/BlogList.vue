<template>
  <div class="blog-list">
    <h1>Blog Posts</h1>
    <div v-if="loading" class="loading">Loading posts...</div>
    <div v-else class="posts-container">
      <div v-if="posts.length === 0" class="no-posts">No blog posts yet.</div>
      <div v-else class="posts-grid">
        <div v-for="post in posts" :key="post.id" class="post-card">
          <h3>{{ post.title }}</h3>
          <p>{{ post.excerpt }}</p>
          <div v-if="post.tags?.length" class="tags">
            <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <router-link :to="`/blog/${post.slug}`" class="read-more">Read More →</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { blog } from '../../services/api'

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await blog.getPosts()
    posts.value = response.data
  } catch (error) {
    console.error('Error loading posts:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style>
.blog-list {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.blog-list h1 {
  margin-bottom: 2rem;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.post-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.post-card h3 {
  margin-bottom: 0.5rem;
}

.tags {
  margin: 1rem 0;
}

.tag {
  background: #3498db;
  color: #fff;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.read-more {
  color: #3498db;
  text-decoration: none;
}

.read-more:hover {
  text-decoration: underline;
}

.loading, .no-posts {
  text-align: center;
  color: #666;
  padding: 2rem;
}
</style>