<template>
  <div
    v-show="isVisible"
    class="modal-overlay"
    @click.self="closeModal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
  >
    <div class="modal-content">
      <button @click="closeModal" class="close-button" aria-label="Close modal">
        x
      </button>

      <header class="modal-header">
        <h2 id="modal-title" class="modal-title">Post Details</h2>
      </header>

      <div class="modal-body">
        <div class="media-section" v-if="post.media_url || post.video_url">
          <img
            v-if="showImage"
            :src="post.media_url"
            :alt="post.text || 'Post image'"
            class="modal-image"
            loading="lazy"
            @error="handleImageError"
          />

          <video
            v-if="showVideo"
            ref="videoRef"
            controls
            preload="metadata"
            class="modal-video"
            @error="handleVideoError"
            @click.stop="playVideo"
          >
            <source :src="post.video_url" type="video/mp4" />
            Your browser does not support the video tag.
          </video>

          <div v-if="!showImage && !showVideo" class="media-placeholder">
            <span class="icon">Media unavailable</span>
          </div>
        </div>

        <div class="content-section">
          <section v-if="post.text" class="post-text-section">
            <h3 class="post-caption">Caption</h3>
            <p class="post-text">{{ post.text }}</p>
          </section>

          <section v-if="post.tags && post.tags.length > 0" class="tags-section">
            <h3 class="section-title">Tags</h3>
            <div class="tags-container">
              <span v-for="tag in post.tags" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>
          </section>

          <section class="metadata-section">
            <h3 class="section-title">Metadata</h3>
            <div class="metadata-grid">
              <div class="metadata-item">
                <span class="label">Author:</span>
                <span class="value">{{ post.author }}</span>
              </div>
              <div class="metadata-item">
                <span class="label">Posted:</span>
                <span class="value" :title="formatTimestamp()">
                  {{ formatRelativeTime() }}
                </span>
              </div>
              <div class="metadata-item">
                <span class="label">Post ID:</span>
                <span class="value">{{ post.id }}</span>
              </div>
            </div>
          </section>
        </div>
      </div>

      <footer class="modal-footer">
        <button @click="closeModal" class="close-btn" aria-label="Close and return to feed">
          Close
        </button>
      </footer>
    </div>
  </div>

  <div v-if="loading" class="modal-loading">
    <div class="spinner"></div>
    <span>Loading post details...</span>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

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

const emit = defineEmits(['close'])

const isVisible = ref(true)
const videoRef = ref(null)
const imageFailed = ref(false)
const videoFailed = ref(false)

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

const closeModal = () => {
  isVisible.value = false
  emit('close')
}

onMounted(() => {
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background-color: var(--bg-white, #fff);
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
  position: relative;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-muted, #999);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
  z-index: 10;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.1);
  color: var(--text-primary, #333);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #eee);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin: 0;
}

.modal-body {
  padding: 0;
}

.media-section {
  width: 100%;
  background-color: var(--bg-secondary, #f9f9f9);
}

.modal-image {
  display: block;
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}

.modal-video {
  width: 100%;
  max-height: 400px;
  background-color: #000;
}

.media-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.content-section {
  padding: 20px 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted, #999);
  margin-bottom: 12px;
  text-transform: uppercase;
}

.post-text-section .post-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary, #333);
  margin-bottom: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background-color: var(--accent-light, #e8f4fc);
  border-radius: 16px;
  font-size: 13px;
  color: var(--text-primary, #333);
}

.metadata-grid {
  display: grid;
  gap: 12px;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metadata-item .label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted, #999);
}

.metadata-item .value {
  font-size: 14px;
  color: var(--text-primary, #333);
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color, #eee);
  text-align: center;
}

.close-btn {
  padding: 10px 24px;
  background-color: var(--accent-light, #e8f4fc);
  border: none;
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-primary, #333);
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: var(--accent-color, #4a90d9);
  color: white;
}

.modal-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 9999;
}

.modal-loading .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color, #ddd);
  border-top-color: var(--accent-color, #4a90d9);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .modal-body {
    padding: 0;
  }

  .content-section {
    padding: 16px;
  }
}
</style>
