<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">Quortol</router-link>
      
      <div class="nav-menu">
        <router-link to="/blog" class="nav-link">Blog</router-link>
        <router-link to="/portfolio" class="nav-link">Portfolio</router-link>
        <router-link to="/agent/dashboard" class="nav-link">Agents</router-link>
        
        <span v-if="authStore.isAuthenticated" class="nav-user">
          {{ authStore.user?.username }}
        </span>
        
        <button v-if="authStore.isAuthenticated" @click="logout" class="nav-btn">
          Logout
        </button>
        
        <router-link v-if="!authStore.isAuthenticated" to="/agent/login" class="nav-btn">
          Agent Login
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { auth } from '../services/api'

const authStore = useAuthStore()

const logout = async () => {
  try {
    await auth.logout()
    authStore.logout()
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>

<style>
.navbar {
  background-color: #2c3e50;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  color: #fff;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
}

.nav-menu {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  transition: opacity 0.3s;
}

.nav-link:hover {
  opacity: 0.8;
}

.nav-user {
  color: #fff;
  margin-right: 1rem;
}

.nav-btn {
  background: transparent;
  color: #fff;
  border: 1px solid #fff;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 4px;
  text-decoration: none;
  transition: all 0.3s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>