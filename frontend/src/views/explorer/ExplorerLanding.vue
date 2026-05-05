<template>
  <div class="explorer-page container-xl py-4 py-md-5">
    <header class="mb-4">
      <p class="kicker mb-2">Explorer</p>
      <h1 class="display-5 mb-2">Research Atlas</h1>
      <p class="intro mb-0">
        Explore live Wikipedia knowledge cards, inspect full articles, and move across Quortol in one editorial flow.
      </p>
    </header>

    <section class="row g-3 mb-3">
      <div class="col-12 col-lg-7">
        <form class="card app-card h-100" @submit.prevent="lookupTopic">
          <div class="card-body">
            <label for="topic-input" class="form-label small text-uppercase app-label">Topic Lookup</label>
            <div class="input-group">
              <input
                id="topic-input"
                v-model.trim="topicQuery"
                type="text"
                class="form-control app-control"
                placeholder="Try: Deep sea, Harlem Renaissance, CRISPR"
              />
              <button type="submit" class="btn app-btn" :disabled="pageLoading">
                {{ pageLoading ? 'Searching...' : 'Open Page' }}
              </button>
            </div>
          </div>
        </form>
      </div>
      <div class="col-12 col-lg-5">
        <div class="card app-card h-100">
          <div class="card-body">
            <label for="seed-input" class="form-label small text-uppercase app-label">Feed Seed (optional)</label>
            <input
              id="seed-input"
              v-model.trim="seedTopic"
              type="text"
              class="form-control app-control"
              placeholder="Seed feed by a theme"
            />
            <button class="btn btn-outline-secondary w-100 mt-3 app-btn-outline" :disabled="feedLoading" @click="refreshFeed">
              {{ feedLoading ? 'Refreshing...' : 'Refresh Feed' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <div v-if="errorMessage" class="alert app-alert mb-3" role="alert">{{ errorMessage }}</div>

    <main class="row g-3">
      <section class="col-12 col-xl-4">
        <div class="card app-card h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-baseline mb-2">
              <h2 class="h5 mb-0">Live Feed</h2>
              <span class="text-muted small">{{ feedItems.length }} cards</span>
            </div>

            <div v-if="feedLoading && feedItems.length === 0" class="d-grid gap-2">
              <div class="skeleton-card" v-for="n in 4" :key="n"></div>
            </div>

            <div v-else class="d-grid gap-2">
              <article
                v-for="(item, index) in feedItems"
                :key="`${item.title}-${index}`"
                class="feed-card"
                @click="openFromFeed(item)"
              >
                <p class="topic mb-1">{{ item.topic }}</p>
                <h3 class="h6 mb-1">{{ item.title }}</h3>
                <p class="mb-0">{{ clipped(item.summary, 200) }}</p>
              </article>
            </div>

            <button class="btn app-btn w-100 mt-3" :disabled="feedLoading" @click="loadMoreFeed">
              {{ feedLoading ? 'Loading...' : 'Load More' }}
            </button>
          </div>
        </div>
      </section>

      <section class="col-12 col-xl-8">
        <div class="card app-card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-baseline mb-2">
              <h2 class="h5 mb-0">Article Detail</h2>
              <span v-if="activeArticle" class="text-muted small text-truncate ms-3">{{ activeArticle.title }}</span>
            </div>

            <div v-if="pageLoading" class="empty-state">Loading article...</div>
            <div v-else-if="!activeArticle" class="empty-state">Select a card or search a topic to inspect details.</div>
            <article v-else class="article">
              <h3 class="h4">{{ activeArticle.title }}</h3>
              <p class="summary">{{ activeArticle.summary }}</p>

              <div v-if="activeArticle.images?.length" class="row g-2 my-2">
                <div v-for="(image, index) in activeArticle.images.slice(0, 4)" :key="`${image}-${index}`" class="col-12 col-md-6">
                  <img
                    :src="image"
                    :alt="`Wikipedia image ${index + 1} for ${activeArticle.title}`"
                    loading="lazy"
                    class="detail-image"
                  />
                </div>
              </div>

              <p class="content mb-3">{{ clipped(activeArticle.content, 2000) }}</p>
              <a class="btn app-btn" :href="activeArticle.source_url" target="_blank" rel="noopener noreferrer">
                Open source article
              </a>
            </article>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { explorerWikipedia } from '../../services/api'

const feedItems = ref([])
const activeArticle = ref(null)
const topicQuery = ref('')
const seedTopic = ref('')
const feedLoading = ref(false)
const pageLoading = ref(false)
const errorMessage = ref('')

const clipped = (value, maxChars) => {
  const text = (value || '').trim()
  if (text.length <= maxChars) return text
  return `${text.slice(0, maxChars).trim()}...`
}

const mergeFeedItems = (items) => {
  const seen = new Set(feedItems.value.map((item) => item.title.toLowerCase()))
  for (const item of items) {
    const key = item.title.toLowerCase()
    if (!seen.has(key)) {
      seen.add(key)
      feedItems.value.push(item)
    }
  }
}

const loadFeed = async ({ reset = false } = {}) => {
  feedLoading.value = true
  errorMessage.value = ''

  try {
    const response = await explorerWikipedia.getFeed({
      count: 6,
      seed_topic: seedTopic.value || undefined
    })
    const items = response.data?.data?.items || []
    if (reset) feedItems.value = []
    mergeFeedItems(items)
    if (!activeArticle.value && feedItems.value.length > 0) {
      activeArticle.value = feedItems.value[0]
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Unable to load Wikipedia feed right now.'
  } finally {
    feedLoading.value = false
  }
}

const refreshFeed = async () => {
  await loadFeed({ reset: true })
}

const loadMoreFeed = async () => {
  await loadFeed({ reset: false })
}

const lookupTopic = async () => {
  if (!topicQuery.value) {
    errorMessage.value = 'Please enter a topic to search.'
    return
  }

  pageLoading.value = true
  errorMessage.value = ''

  try {
    const response = await explorerWikipedia.getPage(topicQuery.value)
    activeArticle.value = response.data?.data
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Topic lookup failed.'
  } finally {
    pageLoading.value = false
  }
}

const openFromFeed = (item) => {
  activeArticle.value = item
}

onMounted(async () => {
  await loadFeed({ reset: true })
})
</script>

<style scoped>
.kicker {
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-soft);
  font-size: 0.75rem;
}

.intro {
  color: var(--ink-muted);
  max-width: 66ch;
  line-height: 1.55;
}

.app-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 4px;
}

.app-label {
  color: var(--ink-soft);
  letter-spacing: 0.06em;
}

.app-control {
  border-color: #cfc5b6;
  background: #fcfaf6;
  color: #2f2a23;
}

.app-control::placeholder {
  color: #8f8576;
}

.app-btn {
  border: 1px solid #6a3627;
  background: #6a3627;
  color: #fff;
}

.app-btn:hover {
  border-color: #5e2f22;
  background: #5e2f22;
  color: #fff;
}

.app-btn-outline {
  border-color: #cabfae;
  color: #4d4438;
}

.app-alert {
  color: #a3351f;
  background: #f7e7de;
  border: 1px solid #d5ab98;
}

.feed-card {
  border: 1px solid #d5cbba;
  border-radius: 3px;
  padding: 0.85rem;
  background: #f9f6ef;
  cursor: pointer;
}

.feed-card:hover {
  background: #f1eadf;
}

.topic {
  color: var(--ink-soft);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.feed-card p {
  color: #4f463a;
}

.empty-state {
  min-height: 220px;
  border: 1px dashed #d2c8b8;
  border-radius: 4px;
  display: grid;
  place-items: center;
  color: var(--ink-soft);
  text-align: center;
  padding: 1rem;
}

.summary {
  color: var(--ink-muted);
}

.content {
  line-height: 1.7;
  white-space: pre-line;
  color: #2b2822;
}

.detail-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: 3px;
  border: 1px solid #d7ccbc;
}

.skeleton-card {
  height: 110px;
  border-radius: 3px;
  background: linear-gradient(90deg, rgba(204, 196, 182, 0.25), rgba(204, 196, 182, 0.5), rgba(204, 196, 182, 0.25));
  background-size: 220% 100%;
  animation: shimmer 1.5s infinite linear;
}

@keyframes shimmer {
  from {
    background-position: 220% 0;
  }
  to {
    background-position: -220% 0;
  }
}
</style>
