<template>
  <nav class="navbar navbar-expand-lg sticky-top app-navbar py-3">
    <div class="container-xl">
      <router-link to="/quortol-home" class="navbar-brand app-logo">Quortol</router-link>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#quortol-nav"
        aria-controls="quortol-nav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="quortol-nav" class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-1">
          <li class="nav-item">
            <router-link to="/" class="nav-link">Explorer</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/quortol-home" class="nav-link">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/blog" class="nav-link">Blog</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/portfolio" class="nav-link">Portfolio</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/data-storytelling" class="nav-link">Data Storytelling</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/agent/dashboard" class="nav-link">Agents</router-link>
          </li>
          <li v-if="authStore.isAuthenticated" class="nav-item text-muted small px-lg-2 py-2 py-lg-0">
            {{ authStore.user?.username }}
          </li>
          <li class="nav-item">
            <button v-if="authStore.isAuthenticated" @click="logout" class="btn btn-sm app-btn">Logout</button>
            <router-link v-else to="/agent/login" class="btn btn-sm app-btn">Agent Login</router-link>
          </li>
        </ul>
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

<style scoped>
.app-navbar {
  background: var(--bs-body-bg);
  box-shadow: var(--bs-box-shadow-sm);
}

.app-logo {
  color: #2c2620;
  font-size: 1.45rem;
  font-family: var(--display-font);
  font-weight: 700;
}

.app-logo:hover {
  color: #2c2620;
}

.nav-link {
  color: #534c43;
  border-radius: 3px;
  padding-inline: 0.6rem;
}

.nav-link:hover {
  color: #2f2922;
  box-shadow: inset 0 0 0 1px rgba(120, 100, 71, 0.22);
}

.app-btn {
  background: none;
  border: none;
  color: #6a3627;
  box-shadow: inset 0 0 0 1px rgba(106, 54, 39, 0.48);
}

.app-btn:hover {
  color: #5e2f22;
  box-shadow: inset 0 0 0 1px rgba(94, 47, 34, 0.7);
}
</style>
