<template>
  <div class="essay-page">
    <router-link to="/blog" class="back-link">&larr; Back to Essays</router-link>

    <div v-if="loading" class="loading">Loading post...</div>
    <article v-else-if="post" class="essay">
      <header class="hero">
        <figure v-if="heroImageUrl" class="hero-image">
          <img :src="heroImageUrl" :alt="post.title" />
        </figure>
        <div v-else class="hero-fallback"></div>

        <p v-if="post.tags?.length" class="kicker">{{ post.tags[0].name }}</p>
        <h1 class="title">{{ post.title }}</h1>
        <p class="dek">{{ dek }}</p>

        <div class="meta-row">
          <span>{{ formatDate(post.published_at) }}</span>
          <span>{{ readTime }} min read</span>
          <span>{{ wordCount.toLocaleString() }} words</span>
        </div>

        <div v-if="post.tags?.length" class="tag-row">
          <span v-for="tag in post.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
        </div>
      </header>

      <section class="content" v-html="renderedContent"></section>
    </article>
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

const plainTextContent = computed(() => {
  const content = post.value?.content || ''
  return content
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[>*_~#-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
})

const wordCount = computed(() => {
  if (!plainTextContent.value) return 0
  return plainTextContent.value.split(/\s+/).length
})

const readTime = computed(() => {
  return Math.max(1, Math.round(wordCount.value / 220))
})

const dek = computed(() => {
  const excerpt = post.value?.excerpt?.trim()
  if (excerpt) return excerpt
  if (!plainTextContent.value) return ''
  return `${plainTextContent.value.slice(0, 220).trim()}...`
})

const heroImageUrl = computed(() => {
  const content = post.value?.content || ''
  const markdownImageMatch = content.match(/!\[[^\]]*]\(([^)\s]+)(?:\s+"[^"]*")?\)/)
  if (markdownImageMatch?.[1]) return markdownImageMatch[1]

  const htmlImageMatch = content.match(/<img[^>]+src=["']([^"']+)["']/i)
  if (htmlImageMatch?.[1]) return htmlImageMatch[1]

  return ''
})

const renderedContent = computed(() => {
  if (!post.value?.content) return ''

  return markdownParser.render(post.value.content).replace('<p>', '<p class="lead-paragraph">')
})
</script>

<style scoped>
.essay-page {
  padding: 2.5rem 1.25rem 4rem;
  max-width: 1024px;
  margin: 0 auto;
}

.back-link {
  display: inline-block;
  margin-bottom: 2rem;
  color: var(--ink-soft);
  text-decoration: none;
  letter-spacing: 0.02em;
  font-size: 0.95rem;
}

.back-link:hover {
  color: var(--ink);
}

.hero {
  margin-bottom: 2.75rem;
}

.hero-image {
  margin: 0 0 1.5rem;
  background: #ddd;
  border-radius: 3px;
  overflow: hidden;
}

.hero-image img {
  width: 100%;
  max-height: 60vh;
  object-fit: cover;
  display: block;
}

.hero-fallback {
  height: clamp(220px, 38vw, 400px);
  margin-bottom: 1.5rem;
  border-radius: 3px;
  background:
    radial-gradient(circle at 18% 18%, rgba(255, 255, 255, 0.32), transparent 40%),
    linear-gradient(140deg, #7a8c68 0%, #556d56 38%, #3f524a 100%);
}

.kicker {
  text-transform: uppercase;
  letter-spacing: 0.11em;
  color: var(--ink-soft);
  font-size: 0.76rem;
  margin-bottom: 0.55rem;
}

.title {
  font-size: clamp(2rem, 4vw, 4rem);
  line-height: 1.04;
  margin-bottom: 0.9rem;
}

.dek {
  max-width: 70ch;
  color: var(--ink-muted);
  font-size: clamp(1.05rem, 1.65vw, 1.45rem);
  line-height: 1.45;
}

.meta-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.15rem;
  color: var(--ink-soft);
  font-size: 0.92rem;
}

.meta-row span + span::before {
  content: '•';
  margin-right: 1rem;
}

.tag-row {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  border: 1px solid var(--line);
  color: var(--ink-muted);
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.8rem;
}

.content {
  max-width: 70ch;
  margin: 0 auto;
  font-size: clamp(1.1rem, 1.28vw, 1.36rem);
  line-height: 1.8;
  color: #21201c;
}

.content :deep(h1),
.content :deep(h2),
.content :deep(h3) {
  margin: 2.8rem 0 1rem;
  line-height: 1.14;
}

.content :deep(h2) {
  font-size: clamp(1.65rem, 2.2vw, 2.2rem);
}

.content :deep(h3) {
  font-size: clamp(1.2rem, 1.65vw, 1.6rem);
}

.content :deep(p) {
  margin: 1.25rem 0;
}

.content :deep(.lead-paragraph)::first-letter {
  float: left;
  font-family: var(--display-font);
  font-size: 3.9em;
  line-height: 0.9;
  margin: 0.07em 0.12em 0 0;
  color: #4a3d2b;
}

.content :deep(ul),
.content :deep(ol) {
  margin: 1.2rem 0 1.2rem 1.4rem;
}

.content :deep(li + li) {
  margin-top: 0.5rem;
}

.content :deep(blockquote) {
  margin: 2rem 0;
  padding: 0.25rem 0 0.25rem 1.1rem;
  border-left: 2px solid #a18c67;
  font-family: var(--display-font);
  font-size: 1.15em;
  line-height: 1.5;
  color: #3f372c;
  background: transparent;
}

.content :deep(hr) {
  margin: 2.5rem 0;
  border: 0;
  border-top: 1px solid var(--line);
}

.content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.8rem 0;
  display: block;
  overflow-x: auto;
  font-size: 0.94em;
}

.content :deep(th),
.content :deep(td) {
  border: 1px solid #d8d1c4;
  padding: 0.6rem 0.75rem;
  text-align: left;
}

.content :deep(thead th) {
  background: #f0ece4;
}

.content :deep(code) {
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.88em;
  background: #ebe7de;
}

.content :deep(pre) {
  margin: 1.5rem 0;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  border: 1px solid #ddd3c2;
}

.content :deep(pre code) {
  padding: 0;
  background: transparent;
}

.content :deep(a) {
  color: #7f3a27;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 3px;
  display: block;
  margin: 2rem auto 0.65rem;
}

.loading,
.not-found {
  text-align: center;
  padding: 2rem;
}

.not-found {
  color: #e74c3c;
}

@media (max-width: 768px) {
  .essay-page {
    padding: 1.5rem 1rem 2.5rem;
  }

  .meta-row span + span::before {
    content: '';
    margin: 0;
  }

  .content {
    font-size: 1.08rem;
    line-height: 1.74;
  }
}
</style>
