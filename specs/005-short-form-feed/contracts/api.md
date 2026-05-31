# API Contracts: Short-Form Content Feed

**Branch**: `005-short-form-feed` | **Date**: 2026-05-30 | **Spec**: [spec.md](../specs/005-short-form-feed/spec.md)

## Overview

This document defines the REST API contracts for the short-form content feed. All endpoints are server-side Flask routes called by Vue 3 frontend via Axios HTTP client.

---

## Feed Endpoint

**Endpoint**: `GET /api/short-form/feed`

**Purpose**: Retrieve paginated posts with optional filtering and search.

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | int | ❌ No | 1 | Page number (1-indexed) |
| `limit` | int | ❌ No | 20 | Posts per page (max 100) |
| `tags` | array<string> | ❌ No | [] | Tag filter list (AND logic — post must have ALL selected tags) |
| `keyword` | string | ❌ No | "" | Keyword search across text and tags |

### Response

**Status Code**: `200 OK`

**Content-Type**: `application/json`

**Response Body**:
```json
{
  "posts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Amazing match highlights from yesterday's IPL game! #cricket #ipl",
      "media_url": "backend/static/short_form/images/post_001.jpg",
      "video_url": "backend/static/short_form/videos/post_001.mp4",
      "author": "Sports Desk",
      "timestamp": "2026-05-30T14:30:00Z",
      "tags": ["#cricket", "#ipl", "#match"],
      "created_at": "2026-05-30T14:25:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 50,
    "total_posts": 1000,
    "posts_per_page": 20
  },
  "empty_state": false
}
```

**Empty Feed Response**:
```json
{
  "posts": [],
  "pagination": {
    "current_page": 1,
    "total_pages": 0,
    "total_posts": 0,
    "posts_per_page": 20
  },
  "empty_state": true
}
```

### Error Responses

**Status Code**: `400 Bad Request`

**Trigger**: Invalid query parameters (e.g., `page < 1`, `limit > 100`)

**Response Body**:
```json
{
  "error": "Invalid query parameters",
  "details": {
    "message": "Page must be >= 1 and limit must be <= 100"
  }
}
```

### Implementation Notes

- Posts sorted by `timestamp` descending (reverse chronological order)
- Empty tags array = no tag filtering applied
- Empty keyword = no search applied
- Server validates media existence; broken posts excluded from response
- Pagination uses server-side logic to prevent excessive data transfer

---

## Post Detail Endpoint

**Endpoint**: `GET /api/short-form/posts/{id}`

**Purpose**: Retrieve single post details for modal view.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | ✅ Yes | Post UUID identifier |

### Response

**Status Code**: `200 OK`

**Content-Type**: `application/json`

**Response Body**:
```json
{
  "post": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Amazing match highlights from yesterday's IPL game! #cricket #ipl",
    "media_url": "backend/static/short_form/images/post_001.jpg",
    "video_url": "backend/static/short_form/videos/post_001.mp4",
    "author": "Sports Desk",
    "timestamp": "2026-05-30T14:30:00Z",
    "tags": ["#cricket", "#ipl", "#match"],
    "created_at": "2026-05-30T14:25:00Z"
  }
}
```

### Error Responses

**Status Code**: `404 Not Found`

**Trigger**: Post ID not found in JSON file

**Response Body**:
```json
{
  "error": "Post not found",
  "details": {
    "message": "No post exists with ID: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Status Code**: `400 Bad Request`

**Trigger**: Invalid UUID format in path parameter

**Response Body**:
```json
{
  "error": "Invalid post ID",
  "details": {
    "message": "Post ID must be valid UUID v4 format"
  }
}
```

### Implementation Notes

- Full post metadata returned (no truncation)
- Media URLs are relative to server root (client resolves via `backend/static/short_form/` directory)
- No user interactions included (no likes, comments, shares data)

---

### Vue Frontend Integration Pattern

#### Axios Service Example: Feed Loading

**File**: `frontend/src/api/short-form/feedService.js`

```javascript
import axios from 'axios';

const API_BASE = '/api';

export const feedService = {
  async getFeed(page = 1, limit = 20, tags = [], keyword = '') {
    const params = new URLSearchParams({ page, limit });
    
    if (tags.length > 0) {
      tags.forEach(tag => params.append('tags', tag));
    }
    
    if (keyword) {
      params.append('keyword', keyword);
    }
    
    const response = await axios.get(`${API_BASE}/feed?${params}`);
    return response.data;
  },

  async getPost(id) {
    const response = await axios.get(`${API_BASE}/post/${id}`);
    return response.data.post;
  }
};
```

#### Vue Component Example: Feed Page

**File**: `frontend/src/features/short-form/pages/ShortFormFeedPage\.vue`

```vue
<template>
  <div class="feed-container" ref="scrollContainer">
    <div class="filters">
      <TagFilter v-model="selectedTags" />
      <SearchBar v-model="searchKeyword" @search="handleSearch" />
    </div>

    <PostCard
      v-for="post in posts"
      :key="post.id"
      :post="post"
      @click="openDetailModal(post)"
    />

    <div v-if="loading" class="loading-spinner">Loading...</div>
    <div v-if="!loading && posts.length === 0" class="empty-state">
      <h2>No posts available yet</h2>
      <p>Check back soon for new short-form content!</p>
    </div>

    <!-- Post Detail Modal -->
    <PostModal
      v-if="selectedPost"
      :post="selectedPost"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { feedService } from '@/api/short-form/feedService';

const posts = ref([]);
const selectedTags = ref([]);
const searchKeyword = ref('');
const loading = ref(false);
const selectedPost = ref(null);
const scrollContainer = ref(null);

const loadPosts = async (page) => {
  loading.value = true;
  try {
    const data = await feedService.getFeed(page, 20, selectedTags.value, searchKeyword.value);
    posts.value = page === 1 ? data.posts : [...posts.value, ...data.posts];
  } catch (error) {
    console.error('Failed to load posts:', error);
  } finally {
    loading.value = false;
  }
};

const openDetailModal = (post) => {
  selectedPost.value = post;
};

const closeDetailModal = () => {
  selectedPost.value = null;
};

// Infinite scroll handler
const handleScroll = () => {
  if (!scrollContainer.value) return;
  
  const { scrollTop, scrollHeight, clientHeight } = scrollContainer.value;
  const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100;
  
  if (isNearBottom && !loading.value) {
    const nextPage = Math.floor(posts.value.length / 20) + 1;
    loadPosts(nextPage);
  }
};

onMounted(() => {
  loadPosts(1);
  scrollContainer.value?.addEventListener('scroll', handleScroll);
});
</script>
```

---

## Summary

| Endpoint | Method | Purpose | Status Codes |
|----------|--------|---------|--------------|
| `/api/short-form/feed` | GET | Paginated feed with filters | 200, 400 |
| `/api/short-form/posts/{id}` | GET | Single post details | 200, 404, 400 |

All endpoints are server-side Flask routes. No authentication required (public content). Media files served via static file serving (`flask.send_from_directory`).


