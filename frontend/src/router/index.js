import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { applySEOMetadata } from '../utils/seo'
import Home from '../views/Home.vue'
import ExplorerLanding from '../views/explorer/ExplorerLanding.vue'
import BlogList from '../views/blog/BlogList.vue'
import BlogDetail from '../views/blog/BlogDetail.vue'
import PortfolioList from '../views/portfolio/PortfolioList.vue'
import PortfolioDetail from '../views/portfolio/PortfolioDetail.vue'
import AgentLogin from '../views/agents/AgentLogin.vue'
import AgentDashboard from '../views/agents/AgentDashboard.vue'
import AgentCapabilities from '../views/agents/AgentCapabilities.vue'
import ShortFormFeedPage from '../features/short-form/pages/ShortFormFeedPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/blog'
  },
  {
    path: '/blogs',
    redirect: '/blog'
  },
  {
    path: '/explorer',
    name: 'explorer-landing',
    component: ExplorerLanding,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Explorer | Quortol',
        description: 'Explore live Wikipedia research cards and article summaries in Quortol Explorer.'
      }
    }
  },
  {
    path: '/quortol-home',
    name: 'home',
    component: Home,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Quortol Home',
        description: 'Discover Quortol projects across essays, portfolio work, and interactive data storytelling.'
      }
    }
  },
  {
    path: '/blog',
    name: 'blog',
    component: BlogList,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Quortol Blog',
        description: 'Read Quortol essays on technology, work, policy, and social futures.'
      }
    }
  },
  {
    path: '/blog/:slug',
    name: 'blog-detail',
    component: BlogDetail,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Quortol Blog',
        description: 'Read longform essays from Quortol.'
      }
    }
  },
  {
    path: '/portfolio',
    name: 'portfolio',
    component: PortfolioList,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Portfolio | Quortol',
        description: 'Browse Quortol portfolio projects and technical case studies.'
      }
    }
  },
  {
    path: '/portfolio/:slug',
    name: 'portfolio-detail',
    component: PortfolioDetail,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Portfolio Project | Quortol',
        description: 'Project details from the Quortol portfolio.'
      }
    }
  },
  {
    path: '/agent/login',
    name: 'agent-login',
    component: AgentLogin,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Agent Login | Quortol',
        description: 'Sign in to the Quortol agent workspace.',
        robots: 'noindex,nofollow'
      }
    }
  },
  {
    path: '/agent/dashboard',
    name: 'agent-dashboard',
    component: AgentDashboard,
    meta: {
      requiresAuth: true,
      seo: {
        title: 'Agent Dashboard | Quortol',
        description: 'Private dashboard for Quortol agent operations.',
        robots: 'noindex,nofollow'
      }
    }
  },
  {
    path: '/agent/agents/:agentId/capabilities',
    name: 'agent-capabilities',
    component: AgentCapabilities,
    meta: {
      requiresAuth: true,
      seo: {
        title: 'Agent Capabilities | Quortol',
        description: 'Private capability configuration for Quortol agents.',
        robots: 'noindex,nofollow'
      }
    }
  },
  {
    path: '/data-storytelling',
    name: 'data-storytelling',
    component: () => import('@/views/DataStorytelling.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Data Storytelling | Quortol',
        description: 'Interactive data storytelling dashboards and visual deep dives.'
      }
    }
  },
  {
    path: '/data-storytelling/:dashboard',
    name: 'dashboard-view',
    component: () => import('@/views/DataStorytelling.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Dashboard View | Quortol',
        description: 'Explore interactive dashboard views on Quortol data storytelling.'
      }
    }
  },
  {
    path: '/shorts',
    name: 'short-form-feed',
    component: ShortFormFeedPage,
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Short-Form Content Feed | Quortol',
        description: 'Browse short-form content posts with images, videos, and tags.'
      }
    }
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

router.afterEach((to) => {
  const routeSEO = to.meta?.seo || {}
  applySEOMetadata({
    title: routeSEO.title || 'Quortol',
    description:
      routeSEO.description ||
      'Quortol publishes essays, portfolio work, and data storytelling projects.',
    robots: routeSEO.robots || 'index,follow',
    path: to.path
  })
})

export default router
