<template>
  <article class="post-card" ref="postRef" @click="emit('click')">
    <div class="media-container" v-if="hasMediaContent">
      <img
        v-if="showImage"
        :src="post.media_url"
        :alt="post.text || 'Post image'"
        class="post-image"
        loading="lazy"
        @error="handleImageError"
      />

      <video
        v-if="showVideo"
        ref="videoRef"
        controls
        preload="metadata"
        class="post-video"
        @click.stop="playVideo"
        @error="handleVideoError"
      >
        <source :src="post.video_url" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div v-if="!showImage && !showVideo" class="media-placeholder">
        <span class="icon">Media unavailable</span>
      </div>
    </div>

    <div v-else class="media-placeholder">
      <span class="icon">Text post</span>
    </div>

    <div class="content-section">
      <p v-if="post.text" class="post-text" :class="{ 'has-media': hasMediaContent }">
        {{ post.text }}
      </p>

      <div class="tags-section" v-if="post.tags && post.tags.length > 0">
        <span
          v-for="tag in post.tags"
          :key="tag"
          class="tag"
          @click.stop="emit('filter-tag', tag)"
          tabindex="0"
          role="button"
        >
          {{ tag }}
        </span>
      </div>

      <div class="metadata-section">
        <span class="author">{{ post.author }}</span>
        <span class="timestamp" :title="formatTimestamp()">
          {{ formatRelativeTime() }}
        </span>
      </div>
    </div>

    <div class="engagement-section">
      <div class="metrics-placeholder">
        <span class="info-text">View post details for more info</span>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner">Loading...</div>
  </article>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  post: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click', 'filter-tag'])

const postRef = ref(null)
const videoRef = ref(null)
const imageFailed = ref(false)
const videoFailed = ref(false)

const hasMediaContent = computed(() => Boolean(props.post.media_url || props.post.video_url))
const showImage = computed(() => Boolean(props.post.media_url) && !imageFailed.value)
const showVideo = computed(() => Boolean(props.post.video_url) && !videoFailed.value)

const formatRelativeTime = () => {
  const timestamp = new Date(props.post.timestamp)
  const now = new Date()
  const diffMs = now - timestamp
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`

  return timestamp.toLocaleDateString()
}

const formatTimestamp = () => {
  const timestamp = new Date(props.post.timestamp)
  return timestamp.toLocaleString()
}

const handleImageError = () => {
  imageFailed.value = true
}

const handleVideoError = () => {
  videoFailed.value = true
}

const playVideo = () => {
  if (!videoRef.value) return

  if (videoRef.value.paused) {
    videoRef.value.play()
  } else {
    videoRef.value.pause()
  }
}

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          observer.unobserve(entry.target)
        }
      })
    },
    {
      rootMargin: '50px',
      threshold: 0.1,
    },
  )

  if (postRef.value) {
    observer.observe(postRef.value)
  }
})
</script>

<style scoped>
.post-card {
  background-color: var(--bg-white, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.post-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
}

.media-container {
  position: relative;
  width: 100%;
  background-color: var(--bg-secondary, #f9f9f9);
}

.post-image {
  display: block;
  max-width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
}

.post-video {
  width: 100%;
  max-height: 400px;
  background-color: #000;
}

.media-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  font-size: 14px;
  color: var(--text-muted, #999);
  background-color: var(--bg-secondary, #f9f9f9);
}

.content-section {
  padding: 12px 16px;
}

.post-text {
  font-size: 15px;
  line-height: 1.5;
  color: var(--text-primary, #333);
  margin-bottom: 8px;
}

.post-text.has-media {
  margin-top: 0;
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background-color: var(--accent-light, #e8f4fc);
  border-radius: 16px;
  font-size: 13px;
  color: var(--text-primary, #333);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag:hover {
  background-color: var(--accent-color, #4a90d9);
  color: white;
}

.metadata-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted, #999);
}

.author {
  font-weight: 500;
}

.timestamp {
  white-space: nowrap;
}

.engagement-section {
  padding: 8px 16px;
  border-top: 1px solid var(--border-color, #eee);
}

.metrics-placeholder {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted, #999);
}

.loading-spinner {
  padding: 16px;
  text-align: center;
  color: var(--text-muted, #999);
}

@media (max-width: 768px) {
  .post-image {
    max-height: 300px;
  }

  .post-video {
    max-height: 300px;
  }
}
</style>
