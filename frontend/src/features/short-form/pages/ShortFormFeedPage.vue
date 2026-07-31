<template>
  <div class="feed-container">
    <aside class="filters-sidebar">
      <h2 class="filters-title">Filters</h2>

      <TagFilter
        v-model="selectedTags"
        :available-tags="allTags"
        @change="handleFilterChange"
        class="filter-section"
      />

      <SearchBar
        v-model="searchKeyword"
        @search="handleSearch"
        class="filter-section"
      />

      <button v-if="hasFilters" @click="clearAllFilters" class="clear-filters-btn">
        Clear All Filters
      </button>
    </aside>

    <main ref="feedMain" class="feed-main">
      <h1 class="feed-title">Short-Form Content Feed</h1>

      <div v-if="loading && posts.length === 0" class="loading-state">
        <div class="spinner"></div>
        <p>Loading posts...</p>
      </div>

      <div v-show="!loading || posts.length > 0" class="posts-container">
        <PostCard
          v-for="post in posts"
          :key="post.id"
          :post="post"
          :loading="loading"
          @click="openDetailModal(post)"
          @filter-tag="handleFilterTag"
          class="post-item"
        />

        <div v-if="hasMorePages && !loading" ref="loadTrigger" class="load-trigger"></div>
      </div>

      <div v-if="!loading && posts.length === 0 && !isLoadingData && !loadError" class="empty-state">
        <h2>No posts available yet</h2>
        <p>Check back soon for new short-form content!</p>
      </div>

      <div v-if="loadError" class="feed-error" role="alert">
        <span>{{ loadError }}</span>
        <button type="button" class="retry-btn" @click="retryLoad">Try again</button>
      </div>

      <div v-if="loading && posts.length > 0" class="load-more-spinner">
        <div class="spinner"></div>
        <span>Loading more...</span>
      </div>

      <div v-if="!hasMorePages && !loading && posts.length > 0" class="no-more-posts">
        <span>All posts loaded</span>
      </div>
    </main>

    <PostModal v-if="selectedPost" :post="selectedPost" @close="closeDetailModal" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import PostCard from '../components/PostCard.vue'
import PostModal from '../components/PostModal.vue'
import SearchBar from '../components/SearchBar.vue'
import TagFilter from '../components/TagFilter.vue'
import { feedService } from '../services/feedService'
import { trackEvent } from '../../../services/analytics'

const posts = ref([])
const selectedTags = ref([])
const searchKeyword = ref('')
const loading = ref(false)
const isLoadingData = ref(false)
const selectedPost = ref(null)
const loadTrigger = ref(null)
const feedMain = ref(null)
const loadError = ref('')

const currentPage = ref(1)
const totalPages = ref(0)
const postsPerPage = 20
const allTags = ref([])

let feedObserver = null
let activeController = null
let requestVersion = 0

const hasFilters = computed(() => selectedTags.value.length > 0 || searchKeyword.value.trim() !== '')
const hasMorePages = computed(() => currentPage.value < totalPages.value)

const appendUniquePosts = (existing, incoming) => {
  const seen = new Set(existing.map((post) => post.id))
  return [
    ...existing,
    ...incoming.filter((post) => {
      if (seen.has(post.id)) return false
      seen.add(post.id)
      return true
    }),
  ]
}

const getResultCount = (response) =>
  response?.pagination?.total_posts ?? response?.posts?.length ?? 0

const emitAnalytics = (context, response) => {
  if (!context?.type) {
    return
  }

  const resultCount = getResultCount(response)

  if (context.type === 'search') {
    trackEvent('shorts_search', {
      result_count: resultCount,
      keyword_length: context.keywordLength ?? 0,
    })
    return
  }

  if (context.type === 'filter') {
    trackEvent('shorts_filter_apply', {
      result_count: resultCount,
      tag_count: selectedTags.value.length,
      tags: [...selectedTags.value],
    })
  }
}

const loadPosts = async (page = 1, reset = false, analyticsContext = null) => {
  if (reset) {
    requestVersion += 1
    activeController?.abort()
  } else if (loading.value || isLoadingData.value) {
    return
  }

  const version = requestVersion
  const controller = new AbortController()
  activeController = controller
  loading.value = true
  isLoadingData.value = true
  loadError.value = ''

  try {
    const response = await feedService.getFeed({
      page,
      limit: postsPerPage,
      tags: selectedTags.value,
      keyword: searchKeyword.value.trim(),
      signal: controller.signal,
    })

    if (version !== requestVersion) return

    if (reset) {
      posts.value = response.posts || []
    } else {
      posts.value = appendUniquePosts(posts.value, response.posts || [])
    }

    currentPage.value = response.pagination?.current_page || page
    totalPages.value = response.pagination?.total_pages || 0

    // Keep a stable master tag list; don't collapse options when current filtered result is empty.
    if (allTags.value.length === 0) {
      if (Array.isArray(response.available_tags) && response.available_tags.length > 0) {
        allTags.value = response.available_tags
      } else {
        const tagSet = new Set()
        posts.value.forEach((post) => (post.tags || []).forEach((tag) => tagSet.add(tag)))
        allTags.value = Array.from(tagSet)
      }
    }

    emitAnalytics(analyticsContext, response)
  } catch (error) {
    if (controller.signal.aborted || version !== requestVersion) return
    console.error('Failed to load posts:', error)
    loadError.value = posts.value.length > 0
      ? 'More posts could not be loaded.'
      : 'Posts could not be loaded.'
  } finally {
    if (version === requestVersion) {
      loading.value = false
      isLoadingData.value = false
      if (activeController === controller) activeController = null
    }
  }
}

const resetFeedPosition = () => {
  const scrollTarget = feedMain.value
  if (typeof scrollTarget?.scrollTo === 'function') {
    scrollTarget.scrollTo({ top: 0, behavior: 'auto' })
  } else if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') {
    window.scrollTo({ top: 0, behavior: 'auto' })
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  resetFeedPosition()
  loadPosts(1, true, { type: 'filter' })
}

const handleSearch = (keyword) => {
  searchKeyword.value = keyword
  currentPage.value = 1
  resetFeedPosition()
  loadPosts(1, true, {
    type: 'search',
    keywordLength: keyword.trim().length,
  })
}

const handleFilterTag = (tag) => {
  if (!selectedTags.value.includes(tag)) {
    selectedTags.value = [...selectedTags.value, tag]
    handleFilterChange()
  }
}

const clearAllFilters = () => {
  selectedTags.value = []
  searchKeyword.value = ''
  currentPage.value = 1
  resetFeedPosition()
  loadPosts(1, true, { type: 'filter' })
}

const retryLoad = () => {
  const page = posts.value.length > 0 ? currentPage.value + 1 : 1
  loadPosts(page, posts.value.length === 0)
}

const openDetailModal = (post) => {
  selectedPost.value = post
}

const closeDetailModal = () => {
  selectedPost.value = null
}

const setupObserver = () => {
  if (feedObserver) {
    feedObserver.disconnect()
  }

  feedObserver = new IntersectionObserver((entries) => {
    const [entry] = entries
    if (!entry?.isIntersecting) return
    if (!hasMorePages.value || loading.value) return

    loadPosts(currentPage.value + 1)
  }, { root: null, rootMargin: '240px 0px', threshold: 0.1 })

  if (loadTrigger.value) {
    feedObserver.observe(loadTrigger.value)
  }
}

onMounted(async () => {
  await loadPosts(1)
  setupObserver()
})

watch(loadTrigger, () => {
  setupObserver()
})

watch(hasMorePages, (hasMore) => {
  if (!hasMore) {
    feedObserver?.disconnect()
  } else {
    setupObserver()
  }
})

onUnmounted(() => {
  requestVersion += 1
  activeController?.abort()
  if (feedObserver) {
    feedObserver.disconnect()
  }
})
</script>

<style scoped>
.feed-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-primary, #f5f5f5);
}

.filters-sidebar {
  width: 280px;
  background-color: var(--bg-white, #fff);
  border-right: 1px solid var(--border-color, #ddd);
  padding: 20px;
  overflow-y: auto;
  flex-shrink: 0;
}

.filters-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.clear-filters-btn {
  width: 100%;
  padding: 8px 16px;
  background-color: var(--accent-light, #e8f4fc);
  border: none;
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-primary, #333);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background-color: var(--accent-color, #4a90d9);
  color: white;
}

.feed-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.feed-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color, #ddd);
  border-top-color: var(--accent-color, #4a90d9);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.load-trigger {
  height: 20px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-state h2 {
  font-size: 20px;
  color: var(--text-primary, #333);
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 15px;
  color: var(--text-muted, #999);
}

.load-more-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background-color: var(--bg-white, #fff);
  border-radius: 8px;
}

.load-more-spinner .spinner {
  width: 24px;
  height: 24px;
  border-width: 3px;
}

.no-more-posts {
  text-align: center;
  padding: 16px;
  color: var(--text-muted, #999);
  font-size: 14px;
}

.feed-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  color: #8b2f24;
}

.retry-btn {
  padding: 6px 12px;
  border: 1px solid currentColor;
  border-radius: 4px;
  color: inherit;
  background: transparent;
  cursor: pointer;
}

@media (max-width: 768px) {
  .feed-container {
    flex-direction: column;
  }

  .filters-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border-color, #ddd);
  }

  .feed-main {
    padding: 12px;
  }
}
</style>
