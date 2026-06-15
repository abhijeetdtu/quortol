import Home from '../views/Home.vue'
import ExplorerLanding from '../views/explorer/ExplorerLanding.vue'
import BlogList from '../views/blog/BlogList.vue'
import BlogDetail from '../views/blog/BlogDetail.vue'
import PodcastList from '../views/podcasts/PodcastList.vue'
import PodcastDetail from '../views/podcasts/PodcastDetail.vue'
import PortfolioList from '../views/portfolio/PortfolioList.vue'
import PortfolioDetail from '../views/portfolio/PortfolioDetail.vue'
import AgentLogin from '../views/agents/AgentLogin.vue'
import AgentDashboard from '../views/agents/AgentDashboard.vue'
import AgentCapabilities from '../views/agents/AgentCapabilities.vue'
import ShortFormFeedPage from '../features/short-form/pages/ShortFormFeedPage.vue'
import {
  buildCollectionPageStructuredData,
  buildPodcastSeriesStructuredData,
  buildStaticPageSEOPayload,
  buildWebPageStructuredData,
} from '../utils/seoContent'

const homeDescription =
  'Discover Quortol projects across essays, portfolio work, and interactive data storytelling.'
const blogDescription = 'Read Quortol essays on technology, work, policy, and social futures.'
const portfolioDescription = 'Browse Quortol portfolio projects and technical case studies.'
const podcastDescription =
  'Listen to Quortol podcast episodes adapted from essays and original conversations.'
const explorerDescription =
  'Explore live Wikipedia research cards and article summaries in Quortol Explorer.'
const dataStorytellingDescription =
  'Interactive data storytelling dashboards and visual deep dives.'

export const routes = [
  {
    path: '/',
    redirect: '/blog',
  },
  {
    path: '/blogs',
    redirect: '/blog',
  },
  {
    path: '/explorer',
    name: 'explorer-landing',
    component: ExplorerLanding,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Explorer | Quortol',
        description: explorerDescription,
        path: '/explorer',
        structuredData: [
          buildWebPageStructuredData({
            title: 'Explorer | Quortol',
            description: explorerDescription,
            path: '/explorer',
          }),
        ],
      }),
    },
  },
  {
    path: '/quortol-home',
    name: 'home',
    component: Home,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Quortol Home',
        description: homeDescription,
        path: '/quortol-home',
        structuredData: [
          buildWebPageStructuredData({
            title: 'Quortol Home',
            description: homeDescription,
            path: '/quortol-home',
          }),
        ],
      }),
    },
  },
  {
    path: '/blog',
    name: 'blog',
    component: BlogList,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Quortol Blog',
        description: blogDescription,
        path: '/blog',
        structuredData: [
          buildCollectionPageStructuredData({
            title: 'Quortol Blog',
            description: blogDescription,
            path: '/blog',
          }),
        ],
      }),
    },
  },
  {
    path: '/blog/:slug',
    name: 'blog-detail',
    component: BlogDetail,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Quortol Blog',
        description: 'Read longform essays from Quortol.',
        path: '/blog',
        ogType: 'article',
      }),
    },
  },
  {
    path: '/podcasts',
    name: 'podcast-list',
    component: PodcastList,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Podcasts | Quortol',
        description: podcastDescription,
        path: '/podcasts',
        structuredData: [
          buildPodcastSeriesStructuredData({
            title: 'Quortol Podcast',
            description: podcastDescription,
            path: '/podcasts',
          }),
        ],
      }),
    },
  },
  {
    path: '/podcasts/:slug',
    name: 'podcast-detail',
    component: PodcastDetail,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Podcast Episode | Quortol',
        description: 'Listen to a Quortol podcast episode.',
        path: '/podcasts',
        ogType: 'article',
      }),
    },
  },
  {
    path: '/portfolio',
    name: 'portfolio',
    component: PortfolioList,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Portfolio | Quortol',
        description: portfolioDescription,
        path: '/portfolio',
        structuredData: [
          buildCollectionPageStructuredData({
            title: 'Portfolio | Quortol',
            description: portfolioDescription,
            path: '/portfolio',
          }),
        ],
      }),
    },
  },
  {
    path: '/portfolio/:slug',
    name: 'portfolio-detail',
    component: PortfolioDetail,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Portfolio Project | Quortol',
        description: 'Project details from the Quortol portfolio.',
        path: '/portfolio',
      }),
    },
  },
  {
    path: '/agent/login',
    name: 'agent-login',
    component: AgentLogin,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Agent Login | Quortol',
        description: 'Sign in to the Quortol agent workspace.',
        path: '/agent/login',
        robots: 'noindex,nofollow',
      }),
    },
  },
  {
    path: '/agent/dashboard',
    name: 'agent-dashboard',
    component: AgentDashboard,
    meta: {
      requiresAuth: true,
      seo: buildStaticPageSEOPayload({
        title: 'Agent Dashboard | Quortol',
        description: 'Private dashboard for Quortol agent operations.',
        path: '/agent/dashboard',
        robots: 'noindex,nofollow',
      }),
    },
  },
  {
    path: '/agent/agents/:agentId/capabilities',
    name: 'agent-capabilities',
    component: AgentCapabilities,
    meta: {
      requiresAuth: true,
      seo: buildStaticPageSEOPayload({
        title: 'Agent Capabilities | Quortol',
        description: 'Private capability configuration for Quortol agents.',
        path: '/agent/agents',
        robots: 'noindex,nofollow',
      }),
    },
  },
  {
    path: '/data-storytelling',
    name: 'data-storytelling',
    component: () => import('@/views/DataStorytelling.vue'),
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Data Storytelling | Quortol',
        description: dataStorytellingDescription,
        path: '/data-storytelling',
        structuredData: [
          buildWebPageStructuredData({
            title: 'Data Storytelling | Quortol',
            description: dataStorytellingDescription,
            path: '/data-storytelling',
          }),
        ],
      }),
    },
  },
  {
    path: '/data-storytelling/:dashboard',
    name: 'dashboard-view',
    component: () => import('@/views/DataStorytelling.vue'),
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Dashboard View | Quortol',
        description: 'Interactive dashboard detail view on Quortol.',
        path: '/data-storytelling',
        robots: 'noindex,follow',
      }),
    },
  },
  {
    path: '/shorts',
    name: 'short-form-feed',
    component: ShortFormFeedPage,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: 'Short-Form Content Feed | Quortol',
        description: 'Browse short-form content posts with images, videos, and tags.',
        path: '/shorts',
        robots: 'noindex,follow',
      }),
    },
  },
]
