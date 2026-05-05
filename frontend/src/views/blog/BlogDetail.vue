<template>
  <div class="blog-detail">
    <router-link to="/blog" class="back-link">&larr; Back to Blog</router-link>

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
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { blog } from '../../services/api'

const route = useRoute()
const post = ref(null)
const loading = ref(true)

const slug = computed(() => route.params.slug)

const markdownParser = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`
      } catch (error) {
        console.warn('Code highlight failed:', error)
      }
    }

    return `<pre class="hljs"><code>${markdownParser.utils.escapeHtml(str)}</code></pre>`
  }
})

const defaultLinkRenderer =
  markdownParser.renderer.rules.link_open ||
  ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))

markdownParser.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const href = tokens[idx].attrGet('href')
  if (href && /^(https?:)?\/\//.test(href)) {
    tokens[idx].attrSet('target', '_blank')
    tokens[idx].attrSet('rel', 'noopener noreferrer')
  }
  return defaultLinkRenderer(tokens, idx, options, env, self)
}

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

  return markdownParser.render(post.value.content)
})
</script>

<style scoped>
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

.content :deep(h1),
.content :deep(h2),
.content :deep(h3) {
  margin: 2rem 0 1rem;
  line-height: 1.25;
}

.content :deep(p) {
  margin: 1rem 0;
}

.content :deep(ul),
.content :deep(ol) {
  margin: 1rem 0 1rem 1.5rem;
}

.content :deep(li + li) {
  margin-top: 0.4rem;
}

.content :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 0.75rem 1rem;
  border-left: 4px solid #3498db;
  background: #f6fafe;
}

.content :deep(hr) {
  margin: 2rem 0;
  border: 0;
  border-top: 1px solid #d6dde5;
}

.content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  display: block;
  overflow-x: auto;
}

.content :deep(th),
.content :deep(td) {
  border: 1px solid #d6dde5;
  padding: 0.65rem 0.75rem;
  text-align: left;
}

.content :deep(thead th) {
  background: #f4f7fb;
}

.content :deep(code) {
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.92em;
  background: #f1f4f8;
}

.content :deep(pre) {
  margin: 1.25rem 0;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
}

.content :deep(pre code) {
  padding: 0;
  background: transparent;
}

.content :deep(a) {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.loading,
.not-found {
  text-align: center;
  padding: 2rem;
}

.not-found {
  color: #e74c3c;
}
</style>
