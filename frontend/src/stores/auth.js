import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const sessionStore = typeof window !== 'undefined'
  ? window.sessionStorage
  : {
      getItem: () => null,
      setItem: () => {},
      removeItem: () => {},
    }

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)
  
  const checkAuth = () => {
    const token = sessionStore.getItem('auth_token')
    if (token) {
      isAuthenticated.value = true
      const userData = JSON.parse(sessionStore.getItem('user_data'))
      user.value = userData
    }
  }
  
  const login = (userData) => {
    isAuthenticated.value = true
    user.value = userData
    sessionStore.setItem('auth_token', 'auth_token_placeholder')
    sessionStore.setItem('user_data', JSON.stringify(userData))
  }
  
  const logout = () => {
    isAuthenticated.value = false
    user.value = null
    sessionStore.removeItem('auth_token')
    sessionStore.removeItem('user_data')
  }
  
  return {
    isAuthenticated,
    user,
    checkAuth,
    login,
    logout
  }
})
