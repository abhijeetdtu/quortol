import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)
  
  const checkAuth = () => {
    const token = sessionStorage.getItem('auth_token')
    if (token) {
      isAuthenticated.value = true
      const userData = JSON.parse(sessionStorage.getItem('user_data'))
      user.value = userData
    }
  }
  
  const login = (userData) => {
    isAuthenticated.value = true
    user.value = userData
    sessionStorage.setItem('auth_token', 'auth_token_placeholder')
    sessionStorage.setItem('user_data', JSON.stringify(userData))
  }
  
  const logout = () => {
    isAuthenticated.value = false
    user.value = null
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('user_data')
  }
  
  return {
    isAuthenticated,
    user,
    checkAuth,
    login,
    logout
  }
})