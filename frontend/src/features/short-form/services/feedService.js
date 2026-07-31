import axios from 'axios'

const API_BASE = '/api/short-form'
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

    const response = await axios.get(`${API_BASE}/feed?${queryParams.toString()}`, {
      signal: params.signal,
    })
    return response.data
  },

  async getPost(postId) {
    const response = await axios.get(`${API_BASE}/posts/${postId}`)
    return response.data.post
  },
}

export default feedService
