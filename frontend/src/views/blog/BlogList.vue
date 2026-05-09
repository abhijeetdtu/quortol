<template>
  <div class="essay-index container-xl py-4 py-md-5">
    <header class="masthead mb-4">
      <p class="brand mb-2">Curated</p>
      <h1 class="display-4 mb-2">Essays</h1>
      <p class="deck mb-0">Longform writing on technology, work, and social futures.</p>
    </header>

    <div v-if="loading" class="text-center text-muted py-4">Loading essays...</div>
    <div v-else-if="posts.length === 0" class="text-center text-muted py-4">No blog posts yet.</div>
    <div v-else class="index-content">
      <article class="featured row g-3 g-lg-4 pb-4 mb-4">
        <div class="col-12 col-lg-7">
          <div class="featured-media h-100">
            <img v-if="featuredImage" :src="featuredImage" :alt="featuredPost.title" />
            <div v-else class="media-fallback"></div>
          </div>
        </div>
        <div class="col-12 col-lg-5">
          <div class="featured-copy h-100 d-flex flex-column">
            <p class="type mb-2">{{ primaryTag(featuredPost) }}</p>
            <h2 class="mb-2">{{ featuredPost.title }}</h2>
            <p class="excerpt mb-2">{{ featuredPost.excerpt }}</p>
            <p class="meta mb-2">{{ formatDate(featuredPost.published_at) }} &middot; {{ readTime(featuredPost) }} min read</p>
            <router-link :to="`/blog/${featuredPost.slug}`" class="read-link mt-auto">Read essay</router-link>
          </div>
        </div>
      </article>

      <section class="latest">
        <h3 class="mb-2">Latest</h3>
        <article v-for="post in remainingPosts" :key="post.id" class="story-row row g-3 py-3">
          <div class="col-12 col-md-4 col-lg-3">
            <div class="story-thumb">
              <img v-if="storyImage(post)" :src="storyImage(post)" :alt="post.title" />
              <div v-else class="media-fallback"></div>
            </div>
          </div>
          <div class="col-12 col-md-8 col-lg-9">
            <div class="story-copy">
              <p class="type mb-1">{{ primaryTag(post) }}</p>
              <h4 class="mb-2">{{ post.title }}</h4>
              <p class="excerpt mb-2">{{ post.excerpt }}</p>
              <p class="meta mb-2">{{ formatDate(post.published_at) }} &middot; {{ readTime(post) }} min read</p>
              <router-link :to="`/blog/${post.slug}`" class="read-link">Read essay</router-link>
            </div>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { blog } from '../../services/api'

const posts = ref([])
const loading = ref(true)
const detailsBySlug = ref({})

const featuredPost = computed(() => posts.value[0] || null)
const remainingPosts = computed(() => posts.value.slice(1))

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const extractImageFromContent = (content) => {
  if (!content) return ''
  const markdownImageMatch = content.match(/!\[[^\]]*]\(([^)\s]+)(?:\s+"[^"]*")?\)/)
  if (markdownImageMatch?.[1]) return markdownImageMatch[1]

  const htmlImageMatch = content.match(/<img[^>]+src=["']([^"']+)["']/i)
  if (htmlImageMatch?.[1]) return htmlImageMatch[1]

  return ''
}

const countWords = (text) => {
  if (!text) return 0
  return text
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[>*_~#-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean).length
}

const readTime = (post) => {
  const detail = detailsBySlug.value[post.slug]
  const baseText = detail?.content || post.excerpt || ''
  const words = countWords(baseText)
  return Math.max(1, Math.round(words / 220))
}

const primaryTag = (post) => {
  if (Array.isArray(post.tags) && post.tags.length > 0) return post.tags[0]
  return 'Essay'
}

const storyImage = (post) => {
  const detail = detailsBySlug.value[post.slug]
  return extractImageFromContent(detail?.content || '')
}

const featuredImage = computed(() => {
  if (!featuredPost.value) return ''
  return storyImage(featuredPost.value)
})

onMounted(async () => {
  try {
    const response = await blog.getPosts()
    posts.value = response.data

    const slugs = posts.value.slice(0, 8).map((post) => post.slug)
    const detailEntries = await Promise.all(
      slugs.map(async (slug) => {
        try {
          const detailResponse = await blog.getPost(slug)
          return [slug, detailResponse.data]
        } catch (error) {
          return [slug, null]
        }
      })
    )
    detailsBySlug.value = Object.fromEntries(detailEntries)
  } catch (error) {
    console.error('Error loading posts:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.brand {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.deck {
  color: var(--ink-muted);
  max-width: 68ch;
  font-size: 1.05rem;
}

.featured {
  border-bottom: none;
  margin-bottom: 1.75rem;
}

.featured-media {
  min-height: 300px;
}

.featured-media img,
.story-thumb img {
  width: 100%;
  height: 100%;
  min-height: 160px;
  object-fit: cover;
  display: block;
  border-radius: 2px;
}

.media-fallback {
  --deep-space-blue: #003049ff;
  --flag-red: #d62828ff;
  --vivid-tangerine: #f77f00ff;
  --sunflower-gold: #fcbf49ff;
  --vanilla-custard: #eae2b7ff;
  width: 100%;
  height: 100%;
  min-height: 160px;
  border-radius: 2px;
  background:
    radial-gradient(circle at 18% 20%, rgba(234, 226, 183, 0.34), transparent 42%),
    linear-gradient(142deg, var(--deep-space-blue) 0%, var(--flag-red) 52%, var(--vivid-tangerine) 100%);
  box-shadow: inset 0 0 0 1px rgba(133, 121, 99, 0.28), 0 8px 18px rgba(54, 47, 36, 0.08);
}

.latest .story-row:nth-of-type(3n + 1) .media-fallback {
  background:
    radial-gradient(circle at 82% 18%, rgba(234, 226, 183, 0.28), transparent 43%),
    linear-gradient(136deg, var(--flag-red) 0%, var(--vivid-tangerine) 58%, var(--sunflower-gold) 100%);
}

.latest .story-row:nth-of-type(3n + 2) .media-fallback {
  background:
    radial-gradient(circle at 22% 76%, rgba(234, 226, 183, 0.3), transparent 44%),
    linear-gradient(148deg, var(--deep-space-blue) 0%, var(--flag-red) 55%, var(--vivid-tangerine) 100%);
}

.latest .story-row:nth-of-type(3n + 3) .media-fallback {
  background:
    radial-gradient(circle at 76% 78%, rgba(234, 226, 183, 0.26), transparent 42%),
    linear-gradient(140deg, var(--deep-space-blue) 0%, var(--vivid-tangerine) 52%, var(--sunflower-gold) 100%);
}

.featured-copy h2 {
  font-size: clamp(1.6rem, 2.8vw, 2.8rem);
  line-height: 1.1;
}

.story-row {
  border-top: none;
  background: none;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  padding-left: 0.35rem;
  padding-right: 0.35rem;
  box-shadow: var(--soft-shadow);
}

.type {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-soft);
  font-size: 0.72rem;
}

.story-copy h4 {
  font-size: 1.35rem;
  line-height: 1.18;
}

.excerpt {
  color: var(--ink-muted);
  line-height: 1.55;
}

.meta {
  color: var(--ink-soft);
  font-size: 0.84rem;
}

.read-link {
  color: #7f3a27;
  text-decoration: none;
  font-weight: 600;
}

.read-link:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}
</style>
