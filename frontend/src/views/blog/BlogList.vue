<template>
  <div class="essay-index container-xl py-4 py-md-5">
    <header class="masthead mb-4">
      <p class="brand mb-2">Curated</p>
      <h1 class="display-4 mb-2">Essays</h1>
      <p class="deck mb-0">Longform writing on technology, work, and social futures.</p>
    </header>

    <form class="blog-search mb-4" role="search" @submit.prevent="applySearchNow">
      <label class="visually-hidden" for="blog-search-input">Search essays</label>
      <span class="search-icon" aria-hidden="true">⌕</span>
      <input
        id="blog-search-input"
        v-model="searchInput"
        class="form-control"
        type="search"
        placeholder="Search essays"
        autocomplete="off"
        @input="scheduleSearch"
      />
      <button
        v-if="searchInput"
        class="clear-search"
        type="button"
        aria-label="Clear search"
        @click="clearSearch"
      >
        Clear
      </button>
    </form>

    <div v-if="loading" class="text-center text-muted py-4">Loading essays...</div>
    <div v-else-if="error" class="text-center py-4" role="alert">
      <p class="text-muted mb-3">{{ error }}</p>
      <button class="btn btn-sm app-btn-soft" type="button" @click="loadPage(requestedPage)">
        Try again
      </button>
    </div>
    <div v-else-if="invalidPage" class="text-center text-muted py-4" role="alert">
      This blog page does not exist.
    </div>
    <div v-else-if="posts.length === 0 && activeQuery" class="text-center text-muted py-4">
      No essays found for “{{ activeQuery }}”.
    </div>
    <div v-else-if="posts.length === 0" class="text-center text-muted py-4">No blog posts yet.</div>
    <div v-else class="index-content">
      <article v-if="showFeatured" class="featured row g-3 g-lg-4 pb-4 mb-4">
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
        <h3 class="mb-2">
          <template v-if="activeQuery">Search results for “{{ activeQuery }}” ({{ pagination.total_posts }})</template>
          <template v-else>Latest</template>
        </h3>
        <article v-for="post in listPosts" :key="post.id" class="story-row row g-3 py-3">
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

      <nav v-if="totalPages > 1" class="blog-pagination" aria-label="Blog pages">
        <router-link
          v-if="currentPage > 1"
          class="page-link"
          rel="prev"
          :to="pagePath(currentPage - 1)"
        >
          Previous
        </router-link>
        <span v-else class="page-link disabled" aria-disabled="true">Previous</span>

        <router-link
          v-for="page in visiblePages"
          :key="page"
          class="page-link page-number"
          :class="{ active: page === currentPage }"
          :aria-current="page === currentPage ? 'page' : undefined"
          :to="pagePath(page)"
        >
          {{ page }}
        </router-link>

        <router-link
          v-if="currentPage < totalPages"
          class="page-link"
          rel="next"
          :to="pagePath(currentPage + 1)"
        >
          Next
        </router-link>
        <span v-else class="page-link disabled" aria-disabled="true">Next</span>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePrerenderRouteData } from '../../prerender/context'
import { blog } from '../../services/api'
import { extractHeroImage, extractPlainTextFromMarkdown } from '../../utils/blogContent'

const prerenderRouteData = usePrerenderRouteData()
const route = useRoute()
const router = useRouter()
const PAGE_SIZE = 12
const SEARCH_DEBOUNCE_MS = 300
const posts = ref(prerenderRouteData.value?.posts || [])
const loading = ref(posts.value.length === 0)
const pagination = ref(prerenderRouteData.value?.pagination || {
  current_page: 1,
  total_pages: posts.value.length > 0 ? 1 : 0,
  total_posts: posts.value.length,
  posts_per_page: PAGE_SIZE,
})
const error = ref('')
const activeQuery = computed(() => String(route.query.q || '').trim())
const searchInput = ref(activeQuery.value)
let searchTimer = null
let requestSequence = 0

const featuredPost = computed(() => posts.value[0] || null)
const requestedPage = computed(() => {
  if (route.name !== 'blog-page') return 1
  const raw = String(route.params.page || '')
  return /^\d+$/.test(raw) ? Number(raw) : Number.NaN
})
const currentPage = computed(() => pagination.value.current_page || requestedPage.value || 1)
const totalPages = computed(() => pagination.value.total_pages || 0)
const invalidPage = computed(() =>
  !Number.isInteger(requestedPage.value) ||
  requestedPage.value < 1 ||
  requestedPage.value === 1 && route.name === 'blog-page' ||
  totalPages.value > 0 && requestedPage.value > totalPages.value ||
  pagination.value.total_posts === 0 && requestedPage.value > 1
)
const showFeatured = computed(() => !activeQuery.value && currentPage.value === 1 && Boolean(featuredPost.value))
const listPosts = computed(() => showFeatured.value ? posts.value.slice(1) : posts.value)
const visiblePages = computed(() => {
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  const adjustedStart = Math.max(1, end - 4)
  return Array.from({ length: end - adjustedStart + 1 }, (_, index) => adjustedStart + index)
})

const pagePath = (page) => ({
  path: page === 1 ? '/blog' : `/blog/page/${page}`,
  query: activeQuery.value ? { q: activeQuery.value } : {},
})

const updateSearchRoute = async () => {
  const query = searchInput.value.trim()
  if (query === activeQuery.value && requestedPage.value === 1) return
  await router.push({ path: '/blog', query: query ? { q: query } : {} })
}

const scheduleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(updateSearchRoute, SEARCH_DEBOUNCE_MS)
}

const applySearchNow = async () => {
  clearTimeout(searchTimer)
  await updateSearchRoute()
}

const clearSearch = async () => {
  searchInput.value = ''
  clearTimeout(searchTimer)
  await updateSearchRoute()
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const countWords = (text) => {
  const plainText = extractPlainTextFromMarkdown(text)
  if (!plainText) return 0
  return plainText.split(/\s+/).filter(Boolean).length
}

const readTime = (post) => {
  const words = countWords(post.excerpt || '')
  return Math.max(1, Math.round(words / 220))
}

const primaryTag = (post) => {
  if (Array.isArray(post.tags) && post.tags.length > 0) return post.tags[0]
  return 'Essay'
}

const storyImage = (post) => {
  return extractHeroImage({
    content: '',
    featuredImage: post?.featured_image || '',
  })
}

const featuredImage = computed(() => {
  if (!featuredPost.value) return ''
  return storyImage(featuredPost.value)
})

const loadPage = async (page) => {
  if (!Number.isInteger(page) || page < 1 || (page === 1 && route.name === 'blog-page')) {
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''
  const requestId = ++requestSequence
  try {
    const params = { page, limit: PAGE_SIZE }
    if (activeQuery.value) params.q = activeQuery.value
    const response = await blog.getPosts(params)
    if (requestId !== requestSequence) return
    posts.value = response.data.posts || []
    pagination.value = response.data.pagination || {}
  } catch (loadError) {
    if (requestId !== requestSequence) return
    console.error('Error loading posts:', loadError)
    error.value = 'Essays could not be loaded.'
  } finally {
    if (requestId === requestSequence) loading.value = false
  }
}

onMounted(async () => {
  if (
    !activeQuery.value &&
    posts.value.length > 0 &&
    pagination.value.current_page === requestedPage.value
  ) {
    loading.value = false
    return
  }
  await loadPage(requestedPage.value)
})

watch([requestedPage, activeQuery], async ([page, query], [previousPage, previousQuery]) => {
  if (page === previousPage && query === previousQuery) return
  searchInput.value = query
  await loadPage(page)
  if (!error.value && typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'auto' })
  }
})

onBeforeUnmount(() => clearTimeout(searchTimer))
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

.blog-search {
  position: relative;
  max-width: 42rem;
}

.blog-search .form-control {
  padding-left: 2.5rem;
  padding-right: 4.5rem;
}

.search-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  color: var(--ink-soft);
  transform: translateY(-50%);
  pointer-events: none;
}

.clear-search {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  border: 0;
  color: #7f3a27;
  background: transparent;
  transform: translateY(-50%);
}

.blog-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 2rem;
}

.page-link {
  min-width: 2.25rem;
  padding: 0.45rem 0.7rem;
  border-radius: 4px;
  color: #7f3a27;
  text-align: center;
  text-decoration: none;
  box-shadow: inset 0 0 0 1px rgba(146, 126, 95, 0.25);
}

.page-link.active {
  color: #fff;
  background: #7f3a27;
}

.page-link.disabled {
  color: var(--ink-soft);
  opacity: 0.55;
}
</style>
