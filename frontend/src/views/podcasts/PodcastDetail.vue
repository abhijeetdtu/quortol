<template>
  <div class="podcast-page">
    <router-link to="/podcasts" class="back-link">&larr; Back to Podcasts</router-link>

    <div v-if="loading" class="loading">Loading episode...</div>
    <article v-else-if="episode" class="episode">
      <header class="hero">
        <figure class="hero-image">
          <img :src="heroImageUrl" :alt="episode.title" />
        </figure>

        <p class="kicker">{{ episode.source_type === 'blog' ? 'Essay Adaptation' : 'Podcast' }}</p>
        <h1 class="title">{{ episode.title }}</h1>
        <p class="dek">{{ episode.summary }}</p>

        <div class="meta-row">
          <span>{{ formatDate(episode.published_at) }}</span>
          <span v-if="episode.audio_meta?.duration_seconds">{{ formatDuration(episode.audio_meta.duration_seconds) }}</span>
          <span>{{ episode.audio_meta?.content_type || 'audio/wav' }}</span>
        </div>

        <div class="action-row">
          <a :href="episode.audio_url" class="listen-link">Open audio file</a>
          <router-link
            v-if="episode.related_blog_slug"
            :to="`/blog/${episode.related_blog_slug}`"
            class="related-link"
          >
            Read related essay
          </router-link>
        </div>
      </header>

      <section class="player card app-card mb-4">
        <div class="card-body">
          <audio controls preload="none" class="w-100" :src="episode.audio_url">
            Your browser does not support audio playback.
          </audio>
        </div>
      </section>

      <section class="transcript-section">
        <h2 class="section-title">Transcript</h2>
        <div class="transcript content" v-html="renderedTranscript"></div>
      </section>
    </article>
    <div v-else class="not-found">Podcast episode not found.</div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import { usePrerenderRouteData } from '../../prerender/context'
import { podcast } from '../../services/api'
import { applySEOMetadata } from '../../utils/seo'
import {
  buildDescription,
  buildPodcastEpisodeStructuredData,
} from '../../utils/seoContent'

const route = useRoute()
const prerenderRouteData = usePrerenderRouteData()
const episode = ref(prerenderRouteData.value?.episode || null)
const loading = ref(!episode.value)

const markdownParser = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
})

const heroImageUrl = computed(() => episode.value?.image_url || '/quortol-podcast-cover.svg')
const renderedTranscript = computed(() =>
  markdownParser.render(episode.value?.transcript_markdown || ''),
)

const applyEpisodeSEO = (episodeData) => {
  if (!episodeData) return

  applySEOMetadata({
    title: `${episodeData.title} | Quortol`,
    description: buildDescription(
      episodeData.summary || episodeData.transcript_markdown || '',
      'Listen to a Quortol podcast episode.',
    ),
    path: `/podcasts/${episodeData.slug}`,
    ogType: 'article',
    ogImage: episodeData.image_url || '/quortol-podcast-cover.svg',
    structuredData: [buildPodcastEpisodeStructuredData(episodeData)],
  })
}

const formatDate = (date) =>
  new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

const formatDuration = (durationSeconds) => {
  const totalSeconds = Math.max(0, Math.round(Number(durationSeconds) || 0))
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  if (minutes <= 0) return `${seconds}s`
  return `${minutes}m ${String(seconds).padStart(2, '0')}s`
}

const loadEpisode = async (slug) => {
  if (!slug) return
  if (episode.value?.slug === slug) {
    loading.value = false
    applyEpisodeSEO(episode.value)
    return
  }

  loading.value = true
  try {
    const response = await podcast.getEpisode(slug)
    episode.value = response.data.podcast
    applyEpisodeSEO(episode.value)
  } catch (error) {
    console.error('Error loading podcast episode:', error)
    episode.value = null
    applySEOMetadata({
      title: 'Podcast Episode Not Found | Quortol',
      description: 'The requested podcast episode could not be found.',
      path: `/podcasts/${slug}`,
      robots: 'index,follow',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.slug,
  (slug) => {
    loadEpisode(slug)
  },
  { immediate: true },
)

watch(
  () => episode.value,
  (nextEpisode) => {
    if (nextEpisode && typeof document !== 'undefined') {
      applyEpisodeSEO(nextEpisode)
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.podcast-page {
  max-width: 980px;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 1.5rem;
  color: #7f3a27;
  text-decoration: none;
  font-weight: 600;
}

.hero {
  margin-bottom: 2rem;
}

.hero-image {
  margin-bottom: 1.5rem;
}

.hero-image img {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: var(--soft-shadow);
}

.kicker {
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.76rem;
  color: var(--ink-soft);
}

.title {
  font-size: clamp(2rem, 4vw, 3.8rem);
  line-height: 1.05;
  margin-bottom: 0.85rem;
}

.dek {
  font-size: 1.08rem;
  line-height: 1.65;
  color: var(--ink-muted);
  max-width: 70ch;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  color: var(--ink-soft);
  font-size: 0.88rem;
  margin-top: 1rem;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
}

.listen-link,
.related-link {
  color: #7f3a27;
  text-decoration: none;
  font-weight: 600;
}

.section-title {
  margin-bottom: 1rem;
}

.content :deep(h1),
.content :deep(h2),
.content :deep(h3) {
  margin-top: 2rem;
  margin-bottom: 0.85rem;
}

.content :deep(p),
.content :deep(li) {
  color: #2c2620;
  line-height: 1.8;
}

.loading,
.not-found {
  color: var(--ink-muted);
  padding: 2rem 0;
}
</style>
