import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const sessionStore = typeof window !== 'undefined'
  ? window.sessionStorage
  : {
      getItem: () => null,
    }

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for authentication
api.interceptors.request.use(config => {
  const authStore = useAuthStore()
  const token = sessionStore.getItem('auth_token')
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (typeof window !== 'undefined' && error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/agent/login'
    }
    return Promise.reject(error)
  }
)

// API methods
export const blog = {
  getPosts: () => api.get('/blog/'),
  getPost: (slug) => api.get(`/blog/${slug}`),
  getTags: () => api.get('/blog/tags'),
  getCategories: () => api.get('/blog/categories'),
  createPost: (data) => api.post('/blog/create', data)
}

export const podcast = {
  getEpisodes: () => api.get('/podcasts/'),
  getEpisode: (slug) => api.get(`/podcasts/${slug}`),
}

export const dataStorytelling = {
  getDashboards: () => api.get('/data-storytelling/dashboards'),
}

export const agents = {
  getAgents: () => api.get('/agents/'),
  getAgent: (id) => api.get(`/agents/${id}`),
  execute: (id, capability, params) => api.post(`/agents/${id}/execute`, { capability, params }),
  createAgent: (data) => api.post('/agents/', data)
}

export const auth = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
  getSettings: () => api.get('/auth/settings'),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me')
}

export default api
