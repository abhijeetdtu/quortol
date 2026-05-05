<template>
  <div class="pokhi-page">
    <div class="gradient-orb orb-a"></div>
    <div class="gradient-orb orb-b"></div>

    <header class="pokhi-header">
      <div class="brand">
        <p class="kicker">Pokhi Integration</p>
        <h1>Research Atlas</h1>
        <p class="intro">
          Explore live Wikipedia knowledge cards, inspect full articles, and jump back to the classic Quortol space
          whenever you want.
        </p>
      </div>
      <div class="header-actions">
        <router-link to="/quortol-home" class="chip chip-home">Quortol Home</router-link>
        <router-link to="/blog" class="chip">Blog</router-link>
        <router-link to="/portfolio" class="chip">Portfolio</router-link>
      </div>
    </header>

    <section class="controls">
      <form class="search-box" @submit.prevent="lookupTopic">
        <label for="topic-input">Topic Lookup</label>
        <div class="search-row">
          <input
            id="topic-input"
            v-model.trim="topicQuery"
            type="text"
            placeholder="Try: Deep sea, Harlem Renaissance, CRISPR"
          />
          <button type="submit" :disabled="pageLoading">{{ pageLoading ? 'Searching...' : 'Open Page' }}</button>
        </div>
      </form>

      <div class="feed-controls">
        <label for="seed-input">Feed Seed (optional)</label>
        <input id="seed-input" v-model.trim="seedTopic" type="text" placeholder="Seed feed by a theme" />
        <button class="btn-outline" :disabled="feedLoading" @click="refreshFeed">
          {{ feedLoading ? 'Refreshing...' : 'Refresh Feed' }}
        </button>
      </div>
    </section>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <main class="content-grid">
      <section class="feed-panel">
        <div class="panel-title">
          <h2>Live Feed</h2>
          <span>{{ feedItems.length }} cards</span>
        </div>

        <div v-if="feedLoading && feedItems.length === 0" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 4" :key="n"></div>
        </div>

        <div v-else class="feed-list">
          <article
            v-for="(item, index) in feedItems"
            :key="`${item.title}-${index}`"
            class="feed-card"
            @click="openFromFeed(item)"
          >
            <p class="topic">{{ item.topic }}</p>
            <h3>{{ item.title }}</h3>
            <p>{{ clipped(item.summary, 200) }}</p>
          </article>
        </div>

        <button class="load-more" :disabled="feedLoading" @click="loadMoreFeed">
          {{ feedLoading ? 'Loading...' : 'Load More' }}
        </button>
      </section>

      <section class="detail-panel">
        <div class="panel-title">
          <h2>Article Detail</h2>
          <span v-if="activeArticle">{{ activeArticle.title }}</span>
        </div>

        <div v-if="pageLoading" class="detail-loading">Loading article...</div>
        <div v-else-if="!activeArticle" class="empty-state">Select a card or search a topic to inspect details.</div>
        <article v-else class="article">
          <h3>{{ activeArticle.title }}</h3>
          <p class="summary">{{ activeArticle.summary }}</p>

          <div v-if="activeArticle.images?.length" class="image-grid">
            <img
              v-for="(image, index) in activeArticle.images.slice(0, 4)"
              :key="`${image}-${index}`"
              :src="image"
              :alt="`Wikipedia image ${index + 1} for ${activeArticle.title}`"
              loading="lazy"
            />
          </div>

          <p class="content">{{ clipped(activeArticle.content, 2000) }}</p>
          <a class="source-link" :href="activeArticle.source_url" target="_blank" rel="noopener noreferrer">
            Open Source Article
          </a>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { pokhiWikipedia } from '../../services/api'

const feedItems = ref([])
const activeArticle = ref(null)
const topicQuery = ref('')
const seedTopic = ref('')
const feedLoading = ref(false)
const pageLoading = ref(false)
const errorMessage = ref('')

const clipped = (value, maxChars) => {
  const text = (value || '').trim()
  if (text.length <= maxChars) {
    return text
  }
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
    const response = await pokhiWikipedia.getFeed({
      count: 6,
      seed_topic: seedTopic.value || undefined
    })
    const items = response.data?.data?.items || []
    if (reset) {
      feedItems.value = []
    }
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
    const response = await pokhiWikipedia.getPage(topicQuery.value)
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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Serif:wght@500;700&display=swap');

.pokhi-page {
  --pokhi-bg: #0b1d26;
  --pokhi-panel: rgba(255, 255, 255, 0.08);
  --pokhi-border: rgba(255, 255, 255, 0.18);
  --pokhi-accent: #f5b742;
  --pokhi-accent-2: #43d6b8;
  --pokhi-text: #f7fbff;
  --pokhi-muted: #aac7d9;
  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 3rem;
  background: radial-gradient(circle at 10% 10%, #15404d 0%, #0b1d26 35%, #060f15 100%);
  color: var(--pokhi-text);
  font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(60px);
  opacity: 0.35;
  pointer-events: none;
}

.orb-a {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -80px;
  background: #43d6b8;
}

.orb-b {
  width: 240px;
  height: 240px;
  bottom: -90px;
  right: -50px;
  background: #f5b742;
}

.pokhi-header,
.controls,
.content-grid {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
}

.pokhi-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  align-items: start;
  animation: rise-in 0.45s ease-out;
}

.kicker {
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--pokhi-accent-2);
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.brand h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.8rem);
  font-family: 'IBM Plex Serif', Georgia, serif;
}

.intro {
  margin-top: 0.75rem;
  color: var(--pokhi-muted);
  max-width: 56ch;
}

.header-actions {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.chip {
  border: 1px solid var(--pokhi-border);
  color: var(--pokhi-text);
  text-decoration: none;
  padding: 0.6rem 0.9rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  transition: transform 0.2s ease, background 0.2s ease;
}

.chip:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.15);
}

.chip-home {
  border-color: transparent;
  background: linear-gradient(135deg, var(--pokhi-accent), #e88c1f);
  color: #13242e;
  font-weight: 700;
}

.controls {
  margin-top: 1.8rem;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 1rem;
  animation: rise-in 0.55s ease-out;
}

.search-box,
.feed-controls {
  background: var(--pokhi-panel);
  border: 1px solid var(--pokhi-border);
  border-radius: 16px;
  padding: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: var(--pokhi-muted);
}

.search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.75rem;
}

input {
  width: 100%;
  border: 1px solid var(--pokhi-border);
  border-radius: 12px;
  padding: 0.8rem 0.9rem;
  background: rgba(6, 15, 21, 0.7);
  color: var(--pokhi-text);
}

input::placeholder {
  color: #87a4b5;
}

button {
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, var(--pokhi-accent-2), #2fb797);
  color: #06202a;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  margin-top: 0.75rem;
  border: 1px solid var(--pokhi-border);
  background: transparent;
  color: var(--pokhi-text);
  width: 100%;
}

.error {
  max-width: 1200px;
  margin: 1rem auto 0;
  color: #ffd3ca;
  background: rgba(141, 31, 8, 0.35);
  border: 1px solid rgba(255, 132, 105, 0.45);
  border-radius: 12px;
  padding: 0.65rem 0.9rem;
}

.content-grid {
  margin-top: 1.2rem;
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 1rem;
}

.feed-panel,
.detail-panel {
  background: var(--pokhi-panel);
  border: 1px solid var(--pokhi-border);
  border-radius: 16px;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.panel-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 0.8rem;
}

.panel-title h2 {
  margin: 0;
  font-size: 1.1rem;
}

.panel-title span {
  color: var(--pokhi-muted);
  font-size: 0.85rem;
}

.feed-list {
  display: grid;
  gap: 0.7rem;
}

.feed-card {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 14px;
  padding: 0.9rem;
  background: rgba(5, 21, 31, 0.45);
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease;
  animation: card-in 0.35s ease both;
}

.feed-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 183, 66, 0.65);
}

.topic {
  color: var(--pokhi-accent-2);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.feed-card h3 {
  margin: 0.35rem 0;
  font-size: 1rem;
}

.feed-card p {
  color: #d7eaf5;
  margin: 0;
}

.load-more {
  width: 100%;
  margin-top: 0.8rem;
}

.detail-loading,
.empty-state {
  min-height: 220px;
  border: 1px dashed var(--pokhi-border);
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: var(--pokhi-muted);
  text-align: center;
  padding: 1rem;
}

.article h3 {
  margin-top: 0;
  font-size: clamp(1.4rem, 2vw, 1.9rem);
  font-family: 'IBM Plex Serif', Georgia, serif;
}

.summary {
  color: var(--pokhi-muted);
  margin-bottom: 0.9rem;
}

.content {
  line-height: 1.7;
  white-space: pre-line;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
  margin: 1rem 0;
}

.image-grid img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.source-link {
  display: inline-block;
  margin-top: 0.9rem;
  color: #1a252d;
  background: var(--pokhi-accent);
  text-decoration: none;
  padding: 0.55rem 0.85rem;
  border-radius: 10px;
  font-weight: 700;
}

.skeleton-list {
  display: grid;
  gap: 0.7rem;
}

.skeleton-card {
  height: 110px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.09));
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

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1000px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .controls {
    grid-template-columns: 1fr;
  }

  .pokhi-header {
    grid-template-columns: 1fr;
  }

  .header-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .pokhi-page {
    padding: 1rem 1rem 2rem;
  }

  .search-row {
    grid-template-columns: 1fr;
  }

  .image-grid {
    grid-template-columns: 1fr;
  }
}
</style>
