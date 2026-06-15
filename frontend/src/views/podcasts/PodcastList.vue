<template>
  <div class="podcast-index container-xl py-4 py-md-5">
    <header class="masthead mb-4">
      <p class="brand mb-2">Listen</p>
      <h1 class="display-4 mb-2">Podcasts</h1>
      <p class="deck mb-0">
        Audio conversations adapted from Quortol essays and original podcast episodes.
      </p>
    </header>

    <div v-if="loading" class="text-center text-muted py-4">Loading podcasts...</div>
    <div v-else-if="episodes.length === 0" class="text-center text-muted py-4">
      No podcast episodes published yet.
    </div>
    <div v-else class="index-content">
      <article class="featured row g-3 g-lg-4 pb-4 mb-4">
        <div class="col-12 col-lg-7">
          <div class="featured-media h-100">
            <img :src="featuredEpisode.image_url || defaultImage" :alt="featuredEpisode.title" />
          </div>
        </div>
        <div class="col-12 col-lg-5">
          <div class="featured-copy h-100 d-flex flex-column">
            <p class="type mb-2">{{ sourceLabel(featuredEpisode) }}</p>
            <h2 class="mb-2">{{ featuredEpisode.title }}</h2>
            <p class="excerpt mb-2">{{ featuredEpisode.summary }}</p>
            <p class="meta mb-2">{{ formatDate(featuredEpisode.published_at) }}</p>
            <p v-if="featuredEpisode.related_blog_title" class="related mb-3">
              From essay: {{ featuredEpisode.related_blog_title }}
            </p>
            <router-link :to="`/podcasts/${featuredEpisode.slug}`" class="read-link mt-auto">
              Listen now
            </router-link>
          </div>
        </div>
      </article>

      <section class="latest">
        <h3 class="mb-2">Latest</h3>
        <article
          v-for="episode in remainingEpisodes"
          :key="episode.slug"
          class="story-row row g-3 py-3"
        >
          <div class="col-12 col-md-4 col-lg-3">
            <div class="story-thumb">
              <img :src="episode.image_url || defaultImage" :alt="episode.title" />
            </div>
          </div>
          <div class="col-12 col-md-8 col-lg-9">
            <div class="story-copy">
              <p class="type mb-1">{{ sourceLabel(episode) }}</p>
              <h4 class="mb-2">{{ episode.title }}</h4>
              <p class="excerpt mb-2">{{ episode.summary }}</p>
              <p class="meta mb-2">{{ formatDate(episode.published_at) }}</p>
              <p v-if="episode.related_blog_title" class="related mb-2">
                From essay: {{ episode.related_blog_title }}
              </p>
              <router-link :to="`/podcasts/${episode.slug}`" class="read-link">
                Listen now
              </router-link>
            </div>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePrerenderRouteData } from '../../prerender/context'
import { podcast } from '../../services/api'

const prerenderRouteData = usePrerenderRouteData()
const episodes = ref(prerenderRouteData.value?.podcasts || [])
const loading = ref(episodes.value.length === 0)
const defaultImage = '/quortol-podcast-cover.svg'

const featuredEpisode = computed(() => episodes.value[0] || null)
const remainingEpisodes = computed(() => episodes.value.slice(1))

const formatDate = (date) =>
  new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

const sourceLabel = (episode) => (episode.source_type === 'blog' ? 'Essay Adaptation' : 'Podcast')

onMounted(async () => {
  if (episodes.value.length > 0) {
    loading.value = false
    return
  }

  try {
    const response = await podcast.getEpisodes()
    episodes.value = response.data.podcasts || []
  } catch (error) {
    console.error('Error loading podcasts:', error)
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

.featured-media img,
.story-thumb img {
  width: 100%;
  height: 100%;
  min-height: 180px;
  object-fit: cover;
  display: block;
  border-radius: 8px;
  box-shadow: var(--soft-shadow);
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

.excerpt,
.related {
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
  color: #5e2f22;
}
</style>
