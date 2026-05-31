import axios from 'axios'

const API_BASE = '/api/short-form'
const LEGACY_API_BASE = '/api'

export const feedService = {
  async getFeed(params = {}) {
    const { page = 1, limit = 20, tags = [], keyword = '' } = params

    const queryParams = new URLSearchParams({
      page: String(page),
      limit: String(limit),
    })

    if (Array.isArray(tags) && tags.length > 0) {
      tags.forEach((tag) => queryParams.append('tags', tag))
    }

    if (keyword && keyword.trim()) {
      queryParams.append('keyword', keyword.trim())
    }

    try {
      const response = await axios.get(`${API_BASE}/feed?${queryParams.toString()}`)
      return response.data
    } catch (error) {
      if (error?.response?.status !== 404) {
        throw error
      }

      // Backward-compatible fallback while backend rolls to namespaced routes.
      const legacyResponse = await axios.get(
        `${LEGACY_API_BASE}/feed?${queryParams.toString()}`,
      )
      return legacyResponse.data
    }
  },

  async getPost(postId) {
    try {
      const response = await axios.get(`${API_BASE}/posts/${postId}`)
      return response.data.post
    } catch (error) {
      if (error?.response?.status !== 404) {
        throw error
      }

      const legacyResponse = await axios.get(`${LEGACY_API_BASE}/post/${postId}`)
      return legacyResponse.data.post
    }
  },
}

export default feedService
