import Home from '../views/Home.vue'
import BlogList from '../views/blog/BlogList.vue'
import BlogDetail from '../views/blog/BlogDetail.vue'
import PodcastList from '../views/podcasts/PodcastList.vue'
import PodcastDetail from '../views/podcasts/PodcastDetail.vue'
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
  'Discover Quortol essays, podcasts, short-form posts, and interactive data storytelling.'
const blogDescription = 'Read Quortol essays on technology, work, policy, and social futures.'
const podcastDescription =
  'Listen to Quortol podcast episodes adapted from essays and original conversations.'
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
    component: () => import('@/views/DataStorytellingDetail.vue'),
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
