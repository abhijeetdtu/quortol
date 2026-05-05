import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Home from '../views/Home.vue'
import ExplorerLanding from '../views/explorer/ExplorerLanding.vue'
import BlogList from '../views/blog/BlogList.vue'
import BlogDetail from '../views/blog/BlogDetail.vue'
import PortfolioList from '../views/portfolio/PortfolioList.vue'
import PortfolioDetail from '../views/portfolio/PortfolioDetail.vue'
import AgentLogin from '../views/agents/AgentLogin.vue'
import AgentDashboard from '../views/agents/AgentDashboard.vue'
import AgentCapabilities from '../views/agents/AgentCapabilities.vue'

const routes = [
  {
    path: '/',
    name: 'explorer-landing',
    component: ExplorerLanding,
    meta: { requiresAuth: false }
  },
  {
    path: '/quortol-home',
    name: 'home',
    component: Home,
    meta: { requiresAuth: false }
  },
  {
    path: '/blog',
    name: 'blog',
    component: BlogList,
    meta: { requiresAuth: false }
  },
  {
    path: '/blog/:slug',
    name: 'blog-detail',
    component: BlogDetail,
    meta: { requiresAuth: false }
  },
  {
    path: '/portfolio',
    name: 'portfolio',
    component: PortfolioList,
    meta: { requiresAuth: false }
  },
  {
    path: '/portfolio/:slug',
    name: 'portfolio-detail',
    component: PortfolioDetail,
    meta: { requiresAuth: false }
  },
  {
    path: '/agent/login',
    name: 'agent-login',
    component: AgentLogin,
    meta: { requiresAuth: false }
  },
  {
    path: '/agent/dashboard',
    name: 'agent-dashboard',
    component: AgentDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/agent/agents/:agentId/capabilities',
    name: 'agent-capabilities',
    component: AgentCapabilities,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next({ name: 'agent-login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  next()
})

export default router
