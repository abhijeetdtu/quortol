# Research: Short-Form Content Feed

**Branch**: `005-short-form-feed` | **Date**: 2026-05-30 | **Spec**: [spec.md](../specs/005-short-form-feed/spec.md)

## Phase 0: Research Findings

This document captures the detailed technical decisions and rationale for the short-form content feed feature. For a high-level summary of key decisions, see `plan.md` → "Research Findings" section.

---

---

### Decision 1: Feed Pagination Pattern

**Decision**: Use server-side pagination with query parameters (`?page=1&limit=20`).

**Rationale**: 
- Prevents excessive data transfer when loading large feeds
- Aligns with SC-001 requirement (view 20 posts within 30 seconds)
- Enables efficient filtering and search on server side
- Consistent with Vue 3 + Axios API call patterns

**Alternatives considered**:
- Client-side all-at-once loading — rejected for being inefficient at scale (>1k posts)
- Infinite scroll without pagination — rejected for requiring full dataset upfront
- "Load more" button pagination — rejected for being less intuitive than automatic scroll-triggered loading

**Implementation approach**:
```javascript
// Vue 3 + Axios pattern
const loadPosts = async (page, limit) => {
  const response = await axios.get('/api/short-form/feed', { params: { page, limit } });
  return response.data.posts;
};

// In component
const posts = ref([]);
const loadMore = async () => {
  const nextPage = Math.floor(scrollPosition / 20) + 1;
  posts.value = [...posts.value, ...await loadPosts(nextPage, 20)];
};
```

---

### Decision 2: Tag Filtering UI Pattern

**Decision**: Use Vue 3 `v-select` component (or custom dropdown) with multi-select for tag filtering.

**Rationale**: 
- Consistent with Vue 3 project conventions (feature 001 uses similar patterns)
- Supports search within dropdown for discoverability
- Toggle selection/deselection UX familiar to users
- No new external dependencies required (can use Bootstrap or custom)

**Alternatives considered**:
- Tag cloud component — rejected for being less precise and harder to filter by multiple tags
- Checkbox list — rejected for taking excessive vertical space
- Multi-select with tag pills — chosen but decided on dropdown for cleaner UI

**Implementation approach**:
```vue
<!-- Vue 3 component -->
<template>
  <v-select
    v-model="selectedTags"
    :options="availableTags"
    multiple
    placeholder="Filter by tags..."
    class="tag-filter-dropdown"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/api/short-form/feedService';

const selectedTags = ref([]);
const availableTags = ref([]);

onMounted(async () => {
  const response = await axios.get('/api/tags');
  availableTags.value = response.data.tags.map(t => ({ label: t, value: t }));
});
</script>
```

---

### Decision 3: Media Lazy-Loading Strategy

**Decision**: Implement viewport-based lazy loading using Intersection Observer API for images and videos.

**Rationale**: 
- Reduces initial page weight significantly
- Improves perceived performance for feeds with many posts
- Prevents bandwidth waste on non-viewed content
- Standard pattern for Instagram/TikTok-style feeds
- Native browser support (no external library needed)

**Alternatives considered**:
- Pre-load all media in viewport + off-screen — rejected for being bandwidth-heavy
- Progressive loading (small→large) — rejected for adding complexity without significant benefit
- Vue lazy-loaded images (`<img loading="lazy">`) — chosen Intersection Observer for better control

**Implementation approach**:
```vue
<!-- PostCard.vue -->
<template>
  <div class="post-card" ref="postRef">
    <img 
      v-show="isLoaded"
      :src="mediaUrl"
      alt="Post media"
      class="lazy-image"
    />
    <video 
      v-if="hasVideo"
      ref="videoRef"
      controls
      preload="none"
      @click="playVideo"
    >
      <source :src="videoUrl" type="video/mp4" />
    </video>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const isLoaded = ref(false);
const postRef = ref(null);

onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        loadMedia();
        observer.unobserve(entry.target);
      }
    });
  });
  
  if (postRef.value) observer.observe(postRef.value);
});

const loadMedia = () => {
  isLoaded.value = true;
};
</script>
```

---

### Decision 4: Empty Feed State Handling

**Decision**: Display user-friendly placeholder message when feed is empty.

**Rationale**: 
- Prevents blank/white screen confusion
- Sets clear expectations ("no posts yet")
- Standard UX pattern for content feeds
- Consistent with Vue design tokens and styling

**Alternatives considered**:
- Error message (500) — rejected for being misleading (not a server error)
- Loading spinner indefinitely — rejected for being frustrating
- Minimal "No posts" text — chosen over more complex graphics for simplicity

**Implementation approach**:
```vue
<template>
  <div v-if="posts.length === 0 && !loading" class="empty-state">
    <h2>No posts available yet</h2>
    <p>Check back soon for new short-form content!</p>
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}
</style>
```

---

### Decision 5: Keyword Search Implementation

**Decision**: Implement server-side keyword search with pandas string matching.

**Rationale**: 
- Faster than client-side search for large datasets
- Enables efficient filtering combined with tag filters
- Leverages existing pandas infrastructure (feature 002)
- Supports partial matching for better discoverability

**Alternatives considered**:
- Client-side search only — rejected for being inefficient at scale
- Elasticsearch/Algolia integration — rejected for YAGNI principle (overkill for v1)
- Full-text database indexing — rejected for adding infrastructure complexity

**Implementation approach**:
```python
# Flask API endpoint
@app.route('/api/short-form/feed', methods=['GET'])
def get_feed():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    tags = request.args.getlist('tags')
    keyword = request.args.get('keyword', '')
    
    posts = feed_service.get_posts_paginated(page, limit)
    
    if tags:
        posts = feed_service.filter_by_tags(posts, tags)
    
    if keyword:
        posts = feed_service.search_keyword(posts, keyword)
    
    return jsonify({
        'posts': posts,
        'pagination': {
            'current_page': page,
            'total_pages': math.ceil(len(posts) / limit),
            'total_posts': len(posts),
            'posts_per_page': limit
        }
    })
```

---

### Decision 6: Post Detail View Navigation

**Decision**: Use modal overlay for post details (preserves scroll position).

**Rationale**: 
- Maintains user context in feed
- Faster than page navigation for quick exploration
- Simpler than implementing back-button history management
- Consistent with modern social feed patterns

**Alternatives considered**:
- Page navigation (navigate to /post/{id}) — rejected for losing scroll position
- Inline expandable card — rejected for being visually cluttered
- Side panel drawer — chosen as alternative but modal preferred for focus

**Implementation approach**:
```vue
<!-- ShortFormFeed.vue -->
<template>
  <div class="feed-container">
    <PostCard 
      v-for="post in posts"
      :key="post.id"
      :post="post"
      @click="openDetailModal(post)"
    />
    
    <PostModal
      v-if="selectedPost"
      :post="selectedPost"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';

const selectedPost = ref(null);

const openDetailModal = (post) => {
  selectedPost.value = post;
};

const closeDetailModal = () => {
  selectedPost.value = null;
};
</script>
```

---

## Summary of Technical Decisions

| Decision | Selected Approach | Key Benefit |
|----------|------------------|-------------|
| Pagination | Server-side with `?page&limit` | Efficient data transfer |
| Tag filtering | Vue 3 multi-select dropdown | Familiar UX, no new deps |
| Media loading | Intersection Observer lazy-load | Reduced initial weight |
| Empty state | Placeholder message | Clear expectations |
| Search | Server-side pandas matching | Fast, scalable |
| Detail view | Modal overlay | Preserves context |

All decisions align with Constitution Principle V (Simplicity & Maintainability) — no over-engineering, minimal dependencies, flat structures preferred. Frontend follows Vue 3 best practices from feature 001.



