<template>
  <div class="blog-detail">
    <router-link to="/blog" class="back-link">← Back to Blog</router-link>
    
    <div v-if="loading" class="loading">Loading post...</div>
    <div v-else-if="post" class="post-content">
      <h1>{{ post.title }}</h1>
      <div class="meta">
        <span>Published: {{ formatDate(post.published_at) }}</span>
        <div v-if="post.tags?.length" class="tags">
          <span v-for="tag in post.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
        </div>
      </div>
      
      <div class="content" v-html="renderedContent"></div>
    </div>
    <div v-else class="not-found">Post not found</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { blog } from '../../services/api'

const route = useRoute()
const post = ref(null)
const loading = ref(true)

const slug = computed(() => route.params.slug)

onMounted(async () => {
  try {
    const response = await blog.getPost(slug.value)
    post.value = response.data
  } catch (error) {
    console.error('Error loading post:', error)
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

const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  
  // Simple markdown-like rendering
  let content = post.value.content
  content = content.replace(/^### (.*$)/gm, '<h3>$1</h3>')
  content = content.replace(/^## (.*$)/gm, '<h2>$1</h2>')
  content = content.replace(/^# (.*$)/gm, '<h1>$1</h1>')
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.*?)\*/g, '<em>$1</em>')
  content = content.replace(/\n/g, '<br>')
  
  return content
})
</script>

<style>
.blog-detail {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.back-link {
  display: block;
  margin-bottom: 1rem;
  color: #3498db;
  text-decoration: none;
}

.post-content h1 {
  margin-bottom: 1rem;
}

.meta {
  margin-bottom: 2rem;
  color: #666;
}

.meta .tags {
  margin-top: 0.5rem;
}

.tags .tag {
  background: #3498db;
  color: #fff;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-right: 0.5rem;
  display: inline-block;
}

.content {
  line-height: 1.8;
  font-size: 1.1rem;
}

.content h1, .content h2, .content h3 {
  margin: 2rem 0 1rem;
}

.loading, .not-found {
  text-align: center;
  padding: 2rem;
}

.not-found {
  color: #e74c3c;
}
</style>