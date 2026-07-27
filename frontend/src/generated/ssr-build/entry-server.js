import { renderToString } from "@vue/server-renderer";
import { ref, useSSRContext, resolveComponent, mergeProps, withCtx, createTextVNode, unref, computed, onMounted, inject, onUnmounted, watch, nextTick, reactive, createSSRApp } from "vue";
import { useRoute, useRouter, createRouter, createWebHistory, createMemoryHistory } from "vue-router";
import { defineStore, createPinia } from "pinia";
import { ssrRenderAttrs, ssrRenderComponent, ssrInterpolate, ssrRenderList, ssrRenderAttr, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrRenderStyle, ssrRenderClass } from "vue/server-renderer";
import axios from "axios";
import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
const sessionStore$1 = typeof window !== "undefined" ? window.sessionStorage : {
  getItem: () => null,
  setItem: () => {
  },
  removeItem: () => {
  }
};
const useAuthStore = defineStore("auth", () => {
  const isAuthenticated = ref(false);
  const user = ref(null);
  const checkAuth = () => {
    const token = sessionStore$1.getItem("auth_token");
    if (token) {
      isAuthenticated.value = true;
      const userData = JSON.parse(sessionStore$1.getItem("user_data"));
      user.value = userData;
    }
  };
  const login = (userData) => {
    isAuthenticated.value = true;
    user.value = userData;
    sessionStore$1.setItem("auth_token", "auth_token_placeholder");
    sessionStore$1.setItem("user_data", JSON.stringify(userData));
  };
  const logout = () => {
    isAuthenticated.value = false;
    user.value = null;
    sessionStore$1.removeItem("auth_token");
    sessionStore$1.removeItem("user_data");
  };
  return {
    isAuthenticated,
    user,
    checkAuth,
    login,
    logout
  };
});
const sessionStore = typeof window !== "undefined" ? window.sessionStorage : {
  getItem: () => null
};
const api = axios.create({
  baseURL: "/api",
  timeout: 3e4,
  headers: {
    "Content-Type": "application/json"
  }
});
api.interceptors.request.use((config) => {
  useAuthStore();
  const token = sessionStore.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
api.interceptors.response.use(
  (response) => response,
  (error) => {
    var _a;
    if (typeof window !== "undefined" && ((_a = error.response) == null ? void 0 : _a.status) === 401) {
      const authStore = useAuthStore();
      authStore.logout();
      window.location.href = "/agent/login";
    }
    return Promise.reject(error);
  }
);
const blog = {
  getPosts: () => api.get("/blog/"),
  getPost: (slug) => api.get(`/blog/${slug}`),
  getTags: () => api.get("/blog/tags"),
  getCategories: () => api.get("/blog/categories"),
  createPost: (data) => api.post("/blog/create", data)
};
const podcast = {
  getEpisodes: () => api.get("/podcasts/"),
  getEpisode: (slug) => api.get(`/podcasts/${slug}`)
};
const dataStorytelling = {
  getDashboards: () => api.get("/data-storytelling/dashboards")
};
const agents = {
  getAgents: () => api.get("/agents/"),
  getAgent: (id) => api.get(`/agents/${id}`),
  execute: (id, capability, params) => api.post(`/agents/${id}/execute`, { capability, params }),
  createAgent: (data) => api.post("/agents/", data)
};
const auth = {
  login: (username, password) => api.post("/auth/login", { username, password }),
  register: (username, email, password) => api.post("/auth/register", { username, email, password }),
  getSettings: () => api.get("/auth/settings"),
  logout: () => api.post("/auth/logout"),
  getCurrentUser: () => api.get("/auth/me")
};
const Navbar_vue_vue_type_style_index_0_scoped_30dc02b2_lang = "";
const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};
const _sfc_main$h = {
  __name: "Navbar",
  __ssrInlineRender: true,
  setup(__props) {
    const authStore = useAuthStore();
    return (_ctx, _push, _parent, _attrs) => {
      var _a;
      const _component_router_link = resolveComponent("router-link");
      _push(`<nav${ssrRenderAttrs(mergeProps({ class: "navbar navbar-expand-lg sticky-top app-navbar py-3" }, _attrs))} data-v-30dc02b2><div class="container-xl" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/quortol-home",
        class: "navbar-brand app-logo"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Quortol`);
          } else {
            return [
              createTextVNode("Quortol")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#quortol-nav" aria-controls="quortol-nav" aria-expanded="false" aria-label="Toggle navigation" data-v-30dc02b2><span class="navbar-toggler-icon" data-v-30dc02b2></span></button><div id="quortol-nav" class="collapse navbar-collapse" data-v-30dc02b2><ul class="navbar-nav ms-auto align-items-lg-center gap-lg-1" data-v-30dc02b2><li class="nav-item" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/quortol-home",
        class: "nav-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Home`);
          } else {
            return [
              createTextVNode("Home")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`</li><li class="nav-item" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/blog",
        class: "nav-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Blog`);
          } else {
            return [
              createTextVNode("Blog")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`</li><li class="nav-item" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/shorts",
        class: "nav-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Shorts`);
          } else {
            return [
              createTextVNode("Shorts")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`</li><li class="nav-item" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/podcasts",
        class: "nav-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Podcasts`);
          } else {
            return [
              createTextVNode("Podcasts")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`</li><li class="nav-item" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/data-storytelling",
        class: "nav-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Data Storytelling`);
          } else {
            return [
              createTextVNode("Data Storytelling")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`</li><li class="nav-item" data-v-30dc02b2>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/agent/dashboard",
        class: "nav-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Agents`);
          } else {
            return [
              createTextVNode("Agents")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(`</li>`);
      if (unref(authStore).isAuthenticated) {
        _push(`<li class="nav-item text-muted small px-lg-2 py-2 py-lg-0" data-v-30dc02b2>${ssrInterpolate((_a = unref(authStore).user) == null ? void 0 : _a.username)}</li>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<li class="nav-item" data-v-30dc02b2>`);
      if (unref(authStore).isAuthenticated) {
        _push(`<button class="btn btn-sm app-btn" data-v-30dc02b2>Logout</button>`);
      } else {
        _push(ssrRenderComponent(_component_router_link, {
          to: "/agent/login",
          class: "btn btn-sm app-btn"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`Agent Login`);
            } else {
              return [
                createTextVNode("Agent Login")
              ];
            }
          }),
          _: 1
          /* STABLE */
        }, _parent));
      }
      _push(`</li></ul></div></div></nav>`);
    };
  }
};
const _sfc_setup$h = _sfc_main$h.setup;
_sfc_main$h.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/components/Navbar.vue");
  return _sfc_setup$h ? _sfc_setup$h(props, ctx) : void 0;
};
const Navbar = /* @__PURE__ */ _export_sfc(_sfc_main$h, [["__scopeId", "data-v-30dc02b2"]]);
const Footer_vue_vue_type_style_index_0_scoped_8a6bde83_lang = "";
const _sfc_main$g = {};
function _sfc_ssrRender(_ctx, _push, _parent, _attrs) {
  _push(`<footer${ssrRenderAttrs(mergeProps({ class: "app-footer py-3 mt-auto" }, _attrs))} data-v-8a6bde83><div class="container-xl text-center small" data-v-8a6bde83><p class="mb-0" data-v-8a6bde83>© 2026 Quortol. All rights reserved.</p></div></footer>`);
}
const _sfc_setup$g = _sfc_main$g.setup;
_sfc_main$g.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/components/Footer.vue");
  return _sfc_setup$g ? _sfc_setup$g(props, ctx) : void 0;
};
const Footer = /* @__PURE__ */ _export_sfc(_sfc_main$g, [["ssrRender", _sfc_ssrRender], ["__scopeId", "data-v-8a6bde83"]]);
const App_vue_vue_type_style_index_0_lang = "";
const _sfc_main$f = {
  __name: "App",
  __ssrInlineRender: true,
  setup(__props) {
    const authStore = useAuthStore();
    const route = useRoute();
    const hideShell = computed(() => {
      var _a;
      return Boolean((_a = route.meta) == null ? void 0 : _a.hideShell);
    });
    onMounted(() => {
      authStore.checkAuth();
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_router_view = resolveComponent("router-view");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "app-shell" }, _attrs))}>`);
      if (!hideShell.value) {
        _push(ssrRenderComponent(Navbar, null, null, _parent));
      } else {
        _push(`<!---->`);
      }
      _push(`<main>`);
      _push(ssrRenderComponent(_component_router_view, null, null, _parent));
      _push(`</main>`);
      if (!hideShell.value) {
        _push(ssrRenderComponent(Footer, null, null, _parent));
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$f = _sfc_main$f.setup;
_sfc_main$f.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/App.vue");
  return _sfc_setup$f ? _sfc_setup$f(props, ctx) : void 0;
};
const PRERENDER_CONTEXT_KEY = Symbol("quortol-prerender-context");
const readClientPrerenderPayload = () => {
  if (typeof window === "undefined") {
    return null;
  }
  return window.__QUORTOL_PRERENDER__ || null;
};
const usePrerenderRouteData = () => {
  const route = useRoute();
  const context = inject(PRERENDER_CONTEXT_KEY, null);
  return computed(() => {
    if (!context || !context.path || context.path !== route.path) {
      return null;
    }
    return context.routeData || null;
  });
};
const BLOCKED_EVENT_KEYS = /* @__PURE__ */ new Set([
  "href",
  "keyword",
  "query",
  "search",
  "searchquery",
  "searchterm",
  "search_query",
  "search_term",
  "url"
]);
const isPublicAnalyticsPath = (path = "") => typeof path === "string" && path.length > 0 && !path.startsWith("/agent/");
const sanitizeEventData = (data = {}) => {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return {};
  }
  return Object.entries(data).reduce((result, [key, value]) => {
    const normalizedKey = String(key || "").replace(/[^a-z0-9]/gi, "").toLowerCase();
    if (BLOCKED_EVENT_KEYS.has(normalizedKey) || value === void 0) {
      return result;
    }
    result[key] = value;
    return result;
  }, {});
};
const withTracker = async (callback) => {
  {
    return false;
  }
};
const trackPageview = () => withTracker();
const trackEvent = (eventName, data = {}) => {
  sanitizeEventData(data);
  return withTracker();
};
const CANONICAL_ORIGIN = "https://quortol.pokhi.in";
const DEFAULT_SEO_DESCRIPTION = "Quortol publishes essays, podcasts, short-form posts, and data storytelling projects.";
const ensureAbsoluteUrl = (value = "/") => {
  if (!value)
    return CANONICAL_ORIGIN;
  if (/^https?:\/\//i.test(value))
    return value;
  const normalizedPath = value.startsWith("/") ? value : `/${value}`;
  return `${CANONICAL_ORIGIN}${normalizedPath}`;
};
const extractPlainText = (value = "") => {
  return String(value || "").replace(/```[\s\S]*?```/g, " ").replace(/`[^`]*`/g, " ").replace(/!\[[^\]]*]\([^)]+\)/g, " ").replace(/\[[^\]]*]\([^)]+\)/g, " ").replace(/<[^>]+>/g, " ").replace(/[>*_~#-]/g, " ").replace(/\s+/g, " ").trim();
};
const buildDescription = (value = "", fallback = DEFAULT_SEO_DESCRIPTION) => {
  const clean = extractPlainText(value);
  if (!clean)
    return fallback;
  if (clean.length <= 160)
    return clean;
  return `${clean.slice(0, 157).trim()}...`;
};
const buildItemList = (items = []) => {
  return items.map((item, index) => ({
    "@type": "ListItem",
    position: index + 1,
    name: item.name,
    url: ensureAbsoluteUrl(item.path)
  }));
};
const buildWebPageStructuredData = ({ title, description, path }) => ({
  "@context": "https://schema.org",
  "@type": "WebPage",
  name: title,
  description,
  url: ensureAbsoluteUrl(path)
});
const buildCollectionPageStructuredData = ({
  title,
  description,
  path,
  items = []
}) => {
  const payload = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: title,
    description,
    url: ensureAbsoluteUrl(path)
  };
  const itemListElement = buildItemList(items);
  if (itemListElement.length > 0) {
    payload.mainEntity = {
      "@type": "ItemList",
      itemListElement
    };
  }
  return payload;
};
const buildBlogPostingStructuredData = (post) => {
  const imageUrl = (post == null ? void 0 : post.featured_image) ? ensureAbsoluteUrl(post.featured_image) : void 0;
  const description = buildDescription((post == null ? void 0 : post.excerpt) || (post == null ? void 0 : post.content) || "", "Read longform essays from Quortol.");
  const payload = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: (post == null ? void 0 : post.title) || "Quortol Essay",
    description,
    url: ensureAbsoluteUrl(`/blog/${(post == null ? void 0 : post.slug) || ""}`),
    mainEntityOfPage: ensureAbsoluteUrl(`/blog/${(post == null ? void 0 : post.slug) || ""}`),
    datePublished: (post == null ? void 0 : post.published_at) || void 0,
    dateModified: (post == null ? void 0 : post.updated_at) || (post == null ? void 0 : post.published_at) || void 0,
    author: {
      "@type": "Organization",
      name: "Quortol"
    },
    publisher: {
      "@type": "Organization",
      name: "Quortol"
    }
  };
  if (imageUrl) {
    payload.image = imageUrl;
  }
  return payload;
};
const buildPodcastSeriesStructuredData = ({
  title,
  description,
  path,
  image = "/quortol-podcast-cover.svg"
}) => ({
  "@context": "https://schema.org",
  "@type": "PodcastSeries",
  name: title,
  description,
  url: ensureAbsoluteUrl(path),
  image: ensureAbsoluteUrl(image),
  publisher: {
    "@type": "Organization",
    name: "Quortol"
  }
});
const buildPodcastEpisodeStructuredData = (episode) => {
  var _a;
  const description = buildDescription(
    (episode == null ? void 0 : episode.summary) || (episode == null ? void 0 : episode.transcript_markdown) || "",
    "Listen to a Quortol podcast episode."
  );
  return {
    "@context": "https://schema.org",
    "@type": "PodcastEpisode",
    name: (episode == null ? void 0 : episode.title) || "Quortol Podcast Episode",
    description,
    url: ensureAbsoluteUrl(`/podcasts/${(episode == null ? void 0 : episode.slug) || ""}`),
    datePublished: (episode == null ? void 0 : episode.published_at) || void 0,
    associatedMedia: (episode == null ? void 0 : episode.audio_url) ? {
      "@type": "MediaObject",
      contentUrl: ensureAbsoluteUrl(episode.audio_url),
      encodingFormat: ((_a = episode == null ? void 0 : episode.audio_meta) == null ? void 0 : _a.content_type) || "audio/wav"
    } : void 0,
    partOfSeries: {
      "@type": "PodcastSeries",
      name: "Quortol Podcast",
      url: ensureAbsoluteUrl("/podcasts")
    },
    image: ensureAbsoluteUrl((episode == null ? void 0 : episode.image_url) || "/quortol-podcast-cover.svg")
  };
};
const buildStaticPageSEOPayload = ({
  title,
  description,
  path,
  structuredData = [],
  robots = "index,follow",
  ogType = "website",
  ogImage = "",
  twitterCard = "summary_large_image"
}) => ({
  title,
  description,
  canonical: ensureAbsoluteUrl(path),
  path,
  robots,
  ogType,
  ogImage,
  twitterCard,
  structuredData
});
const removeElement = (selector) => {
  const element = document.head.querySelector(selector);
  if (element) {
    element.remove();
  }
};
const upsertMetaTag = ({ name, property, content }) => {
  const selector = name ? `meta[name="${name}"]` : `meta[property="${property}"]`;
  if (!content) {
    removeElement(selector);
    return;
  }
  let element = document.head.querySelector(selector);
  if (!element) {
    element = document.createElement("meta");
    if (name)
      element.setAttribute("name", name);
    if (property)
      element.setAttribute("property", property);
    document.head.appendChild(element);
  }
  element.setAttribute("content", content);
};
const upsertCanonicalLink = (href) => {
  let element = document.head.querySelector('link[rel="canonical"]');
  if (!element) {
    element = document.createElement("link");
    element.setAttribute("rel", "canonical");
    document.head.appendChild(element);
  }
  element.setAttribute("href", href);
};
const upsertStructuredData = (structuredData) => {
  document.head.querySelectorAll('script[data-quortol-seo="structured-data"]').forEach((element) => element.remove());
  const entries = Array.isArray(structuredData) ? structuredData.filter(Boolean) : structuredData ? [structuredData] : [];
  for (const entry of entries) {
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.dataset.quortolSeo = "structured-data";
    script.textContent = JSON.stringify(entry);
    document.head.appendChild(script);
  }
};
const applySEOMetadata = ({
  title = "Quortol",
  description = "Quortol publishes essays, podcasts, short-form posts, and data storytelling projects.",
  path = "/",
  canonical,
  robots = "index,follow",
  ogType = "website",
  ogImage = "",
  twitterCard = "summary_large_image",
  structuredData = []
} = {}) => {
  if (typeof document === "undefined") {
    return;
  }
  const canonicalUrl = ensureAbsoluteUrl(canonical || path || "/");
  const imageUrl = ogImage ? ensureAbsoluteUrl(ogImage) : "";
  document.title = title;
  upsertCanonicalLink(canonicalUrl);
  upsertMetaTag({ name: "description", content: description });
  upsertMetaTag({ name: "robots", content: robots });
  upsertMetaTag({ property: "og:title", content: title });
  upsertMetaTag({ property: "og:description", content: description });
  upsertMetaTag({ property: "og:type", content: ogType });
  upsertMetaTag({ property: "og:url", content: canonicalUrl });
  upsertMetaTag({ property: "og:image", content: imageUrl });
  upsertMetaTag({ name: "twitter:card", content: twitterCard });
  upsertMetaTag({ name: "twitter:title", content: title });
  upsertMetaTag({ name: "twitter:description", content: description });
  upsertMetaTag({ name: "twitter:image", content: imageUrl });
  upsertStructuredData(structuredData);
};
const Home_vue_vue_type_style_index_0_scoped_cb0e5bea_lang = "";
const _sfc_main$e = {
  __name: "Home",
  __ssrInlineRender: true,
  setup(__props) {
    var _a;
    const authStore = useAuthStore();
    const prerenderRouteData = usePrerenderRouteData();
    const posts = ref(((_a = prerenderRouteData.value) == null ? void 0 : _a.posts) || []);
    onMounted(async () => {
      if (posts.value.length > 0) {
        return;
      }
      try {
        const postsRes = await blog.getPosts();
        posts.value = postsRes.data;
      } catch (error) {
        console.error("Error loading home data:", error);
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "home-page container-xl py-5" }, _attrs))} data-v-cb0e5bea><section class="hero mb-5" data-v-cb0e5bea><p class="kicker mb-2" data-v-cb0e5bea>Curated</p><h1 class="display-5 mb-3" data-v-cb0e5bea>Come satisfy your curiosity</h1><p class="intro mb-4" data-v-cb0e5bea> Browse longform writing, listen to podcasts, explore short-form posts, or jump into agent tooling with one coherent editorial UI. </p><div class="d-flex flex-wrap gap-2" data-v-cb0e5bea>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/blog",
        class: "btn btn-sm app-btn-soft"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Read Blog`);
          } else {
            return [
              createTextVNode("Read Blog")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(ssrRenderComponent(_component_router_link, {
        to: "/shorts",
        class: "btn btn-sm app-btn-accent"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Browse Shorts`);
          } else {
            return [
              createTextVNode("Browse Shorts")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      _push(ssrRenderComponent(_component_router_link, {
        to: "/podcasts",
        class: "btn btn-sm app-btn-soft"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Listen to Podcasts`);
          } else {
            return [
              createTextVNode("Listen to Podcasts")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      if (!unref(authStore).isAuthenticated) {
        _push(ssrRenderComponent(_component_router_link, {
          to: "/agent/login",
          class: "btn btn-sm app-btn-soft"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(` Access Agents `);
            } else {
              return [
                createTextVNode(" Access Agents ")
              ];
            }
          }),
          _: 1
          /* STABLE */
        }, _parent));
      } else {
        _push(ssrRenderComponent(_component_router_link, {
          to: "/agent/dashboard",
          class: "btn btn-sm app-btn-soft"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`Agent Dashboard`);
            } else {
              return [
                createTextVNode("Agent Dashboard")
              ];
            }
          }),
          _: 1
          /* STABLE */
        }, _parent));
      }
      _push(`</div></section><section class="mb-5" data-v-cb0e5bea><h2 class="mb-3" data-v-cb0e5bea>Latest Essays</h2>`);
      if (posts.value.length === 0) {
        _push(`<div class="text-muted" data-v-cb0e5bea>Loading...</div>`);
      } else {
        _push(`<div class="row g-3" data-v-cb0e5bea><!--[-->`);
        ssrRenderList(posts.value.slice(0, 3), (post) => {
          _push(`<div class="col-12 col-md-6 col-xl-4" data-v-cb0e5bea><article class="card h-100 app-card" data-v-cb0e5bea><div class="card-body" data-v-cb0e5bea><h3 class="h4 card-title" data-v-cb0e5bea>${ssrInterpolate(post.title)}</h3><p class="card-text text-secondary" data-v-cb0e5bea>${ssrInterpolate(post.excerpt)}</p>`);
          _push(ssrRenderComponent(_component_router_link, {
            to: `/blog/${post.slug}`,
            class: "app-link"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(`Read Essay →`);
              } else {
                return [
                  createTextVNode("Read Essay →")
                ];
              }
            }),
            _: 2
            /* DYNAMIC */
          }, _parent));
          _push(`</div></article></div>`);
        });
        _push(`<!--]--></div>`);
      }
      _push(`</section></div>`);
    };
  }
};
const _sfc_setup$e = _sfc_main$e.setup;
_sfc_main$e.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/Home.vue");
  return _sfc_setup$e ? _sfc_setup$e(props, ctx) : void 0;
};
const Home = /* @__PURE__ */ _export_sfc(_sfc_main$e, [["__scopeId", "data-v-cb0e5bea"]]);
const MARKDOWN_IMAGE_PATTERN = /!\[[^\]]*]\(([^)\s]+)(?:\s+"[^"]*")?\)/;
const HTML_IMAGE_PATTERN = /<img[^>]+src=["']([^"']+)["']/i;
const IMAGE_LINE_PATTERN = /^\s*!\[[^\]]*]\([^)]+\)\s*$/;
const HTML_IMAGE_LINE_PATTERN = /^\s*<img[^>]+>\s*$/i;
const HEADING_LINE_PATTERN = /^\s{0,3}#{1,6}\s+/;
const HORIZONTAL_RULE_PATTERN = /^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$/;
const VISUAL_HEADING_PATTERN = /^\s{0,3}#{2,6}\s+visual(?:\s*:?\s*.*)?$/i;
const ITALIC_CAPTION_PATTERN = /^\s*(\*|_).+\1\s*$/;
const LEAD_METADATA_LABELS = ["slug", "author", "date", "published", "updated", "category", "tags", "series", "status"];
const findFirstNonEmptyLineIndex = (lines, start = 0) => {
  for (let index = start; index < lines.length; index += 1) {
    if (lines[index].trim()) {
      return index;
    }
  }
  return -1;
};
const removeLineAndFollowingBlanks = (lines, index) => {
  lines.splice(index, 1);
  while (index < lines.length && lines[index].trim() === "") {
    lines.splice(index, 1);
  }
};
const normalizeComparableText = (value = "") => {
  return value.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/['’"“”]/g, "").replace(/[^a-z0-9]+/g, " ").trim();
};
const escapeForRegex = (value = "") => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const unwrapInlineEmphasis = (line = "") => {
  const trimmed = line.trim();
  const match = trimmed.match(/^(\*{1,3}|_{1,3})(.+)\1$/);
  if (!match)
    return trimmed;
  return (match[2] || "").trim();
};
const isLeadMetadataLine = (line = "") => {
  const trimmed = line.trim();
  const match = trimmed.match(/^\*\*([^*]{1,40}):\*\*\s*.+$/);
  if (!match)
    return false;
  const label = normalizeComparableText(match[1] || "");
  return LEAD_METADATA_LABELS.includes(label);
};
const isImageLine = (line = "") => IMAGE_LINE_PATTERN.test(line) || HTML_IMAGE_LINE_PATTERN.test(line);
const isHeadingLine = (line = "") => HEADING_LINE_PATTERN.test(line);
const isHorizontalRule = (line = "") => HORIZONTAL_RULE_PATTERN.test(line);
const stripDuplicateLeadHeading = (lines, title) => {
  const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines);
  if (firstNonEmptyLineIndex === -1)
    return;
  const headingMatch = lines[firstNonEmptyLineIndex].match(/^#\s+(.+?)\s*$/);
  if (!headingMatch)
    return;
  const headingText = normalizeComparableText(headingMatch[1] || "");
  const titleText = normalizeComparableText(title || "");
  if (!headingText || !titleText || headingText !== titleText)
    return;
  removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex);
};
const stripLeadMetadataLines = (lines) => {
  let removedMetadata = false;
  while (true) {
    const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines);
    if (firstNonEmptyLineIndex === -1) {
      return removedMetadata;
    }
    if (!isLeadMetadataLine(lines[firstNonEmptyLineIndex])) {
      return removedMetadata;
    }
    removedMetadata = true;
    removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex);
  }
};
const stripLeadingRuleAfterMetadata = (lines, removedMetadata) => {
  if (!removedMetadata)
    return;
  while (true) {
    const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines);
    if (firstNonEmptyLineIndex === -1)
      return;
    if (!isHorizontalRule(lines[firstNonEmptyLineIndex]))
      return;
    removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex);
  }
};
const stripDuplicateLeadByline = (lines) => {
  const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines);
  if (firstNonEmptyLineIndex === -1)
    return;
  const candidate = unwrapInlineEmphasis(lines[firstNonEmptyLineIndex] || "");
  if (!/^(by|byline:)\b/i.test(candidate))
    return;
  removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex);
};
const isRedundantVisualHeadingBlock = (lines, headingIndex) => {
  let cursor = findFirstNonEmptyLineIndex(lines, headingIndex + 1);
  if (cursor === -1 || !isImageLine(lines[cursor])) {
    return false;
  }
  cursor = findFirstNonEmptyLineIndex(lines, cursor + 1);
  while (cursor !== -1 && ITALIC_CAPTION_PATTERN.test(lines[cursor].trim())) {
    cursor = findFirstNonEmptyLineIndex(lines, cursor + 1);
  }
  if (cursor === -1) {
    return true;
  }
  return isHorizontalRule(lines[cursor]) || isHeadingLine(lines[cursor]);
};
const stripRedundantVisualHeadings = (lines) => {
  for (let index = 0; index < lines.length; index += 1) {
    if (!VISUAL_HEADING_PATTERN.test(lines[index]))
      continue;
    if (!isRedundantVisualHeadingBlock(lines, index))
      continue;
    lines.splice(index, 1);
    if (index < lines.length && lines[index].trim() === "") {
      lines.splice(index, 1);
    }
    index -= 1;
  }
};
const stripDuplicateHeroImage = (content, heroUrl) => {
  if (!heroUrl)
    return content;
  const escapedUrl = escapeForRegex(heroUrl);
  const markdownPattern = new RegExp(
    `!\\[[^\\]]*\\]\\((?:\\s*<)?${escapedUrl}(?:>)?(?:\\s+["'][^"']*["'])?\\)`,
    "i"
  );
  if (markdownPattern.test(content)) {
    return content.replace(markdownPattern, "").replace(/\n{3,}/g, "\n\n");
  }
  const htmlPattern = new RegExp(`<img[^>]+src=["']${escapedUrl}["'][^>]*>`, "i");
  if (htmlPattern.test(content)) {
    return content.replace(htmlPattern, "").replace(/\n{3,}/g, "\n\n");
  }
  return content;
};
const normalizeMarkdownSpacing = (content = "") => {
  return content.replace(/\r\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
};
const extractHeroImage = ({ content = "", featuredImage = "" } = {}) => {
  if (featuredImage)
    return featuredImage;
  const markdownImageMatch = content.match(MARKDOWN_IMAGE_PATTERN);
  if (markdownImageMatch == null ? void 0 : markdownImageMatch[1])
    return markdownImageMatch[1];
  const htmlImageMatch = content.match(HTML_IMAGE_PATTERN);
  if (htmlImageMatch == null ? void 0 : htmlImageMatch[1])
    return htmlImageMatch[1];
  return "";
};
const extractPlainTextFromMarkdown = (value = "") => {
  return value.replace(/```[\s\S]*?```/g, " ").replace(/`[^`]*`/g, " ").replace(/!\[[^\]]*]\([^)]+\)/g, " ").replace(/\[[^\]]*]\([^)]+\)/g, " ").replace(/<[^>]+>/g, " ").replace(/[>*_~#-]/g, " ").replace(/\s+/g, " ").trim();
};
const sanitizeBlogDisplayContent = ({ content = "", title = "", featuredImage = "" } = {}) => {
  if (!content)
    return "";
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  stripDuplicateLeadHeading(lines, title);
  const removedMetadata = stripLeadMetadataLines(lines);
  stripLeadingRuleAfterMetadata(lines, removedMetadata);
  stripDuplicateLeadByline(lines);
  stripRedundantVisualHeadings(lines);
  const heroImage = extractHeroImage({ content, featuredImage });
  const cleanedContent = stripDuplicateHeroImage(lines.join("\n"), heroImage);
  return normalizeMarkdownSpacing(cleanedContent);
};
const BlogList_vue_vue_type_style_index_0_scoped_57fed79a_lang = "";
const _sfc_main$d = {
  __name: "BlogList",
  __ssrInlineRender: true,
  setup(__props) {
    var _a;
    const prerenderRouteData = usePrerenderRouteData();
    const posts = ref(((_a = prerenderRouteData.value) == null ? void 0 : _a.posts) || []);
    const loading = ref(posts.value.length === 0);
    const detailsBySlug = ref({});
    const featuredPost = computed(() => posts.value[0] || null);
    const remainingPosts = computed(() => posts.value.slice(1));
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric"
      });
    };
    const countWords = (text) => {
      const plainText = extractPlainTextFromMarkdown(text);
      if (!plainText)
        return 0;
      return plainText.split(/\s+/).filter(Boolean).length;
    };
    const readTime = (post) => {
      const detail = detailsBySlug.value[post.slug];
      const baseText = detail ? sanitizeBlogDisplayContent({
        content: detail.content || "",
        title: detail.title || post.title || "",
        featuredImage: detail.featured_image || (post == null ? void 0 : post.featured_image) || ""
      }) : post.excerpt || "";
      const words = countWords(baseText);
      return Math.max(1, Math.round(words / 220));
    };
    const primaryTag = (post) => {
      if (Array.isArray(post.tags) && post.tags.length > 0)
        return post.tags[0];
      return "Essay";
    };
    const storyImage = (post) => {
      const detail = detailsBySlug.value[post.slug];
      return extractHeroImage({
        content: (detail == null ? void 0 : detail.content) || "",
        featuredImage: (detail == null ? void 0 : detail.featured_image) || (post == null ? void 0 : post.featured_image) || ""
      });
    };
    const featuredImage = computed(() => {
      if (!featuredPost.value)
        return "";
      return storyImage(featuredPost.value);
    });
    onMounted(async () => {
      if (posts.value.length > 0) {
        loading.value = false;
        return;
      }
      try {
        const response = await blog.getPosts();
        posts.value = response.data;
        const slugs = posts.value.slice(0, 8).map((post) => post.slug);
        const detailEntries = await Promise.all(
          slugs.map(async (slug) => {
            try {
              const detailResponse = await blog.getPost(slug);
              return [slug, detailResponse.data];
            } catch (error) {
              return [slug, null];
            }
          })
        );
        detailsBySlug.value = Object.fromEntries(detailEntries);
      } catch (error) {
        console.error("Error loading posts:", error);
      } finally {
        loading.value = false;
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "essay-index container-xl py-4 py-md-5" }, _attrs))} data-v-57fed79a><header class="masthead mb-4" data-v-57fed79a><p class="brand mb-2" data-v-57fed79a>Curated</p><h1 class="display-4 mb-2" data-v-57fed79a>Essays</h1><p class="deck mb-0" data-v-57fed79a>Longform writing on technology, work, and social futures.</p></header>`);
      if (loading.value) {
        _push(`<div class="text-center text-muted py-4" data-v-57fed79a>Loading essays...</div>`);
      } else if (posts.value.length === 0) {
        _push(`<div class="text-center text-muted py-4" data-v-57fed79a>No blog posts yet.</div>`);
      } else {
        _push(`<div class="index-content" data-v-57fed79a><article class="featured row g-3 g-lg-4 pb-4 mb-4" data-v-57fed79a><div class="col-12 col-lg-7" data-v-57fed79a><div class="featured-media h-100" data-v-57fed79a>`);
        if (featuredImage.value) {
          _push(`<img${ssrRenderAttr("src", featuredImage.value)}${ssrRenderAttr("alt", featuredPost.value.title)} data-v-57fed79a>`);
        } else {
          _push(`<div class="media-fallback" data-v-57fed79a></div>`);
        }
        _push(`</div></div><div class="col-12 col-lg-5" data-v-57fed79a><div class="featured-copy h-100 d-flex flex-column" data-v-57fed79a><p class="type mb-2" data-v-57fed79a>${ssrInterpolate(primaryTag(featuredPost.value))}</p><h2 class="mb-2" data-v-57fed79a>${ssrInterpolate(featuredPost.value.title)}</h2><p class="excerpt mb-2" data-v-57fed79a>${ssrInterpolate(featuredPost.value.excerpt)}</p><p class="meta mb-2" data-v-57fed79a>${ssrInterpolate(formatDate(featuredPost.value.published_at))} · ${ssrInterpolate(readTime(featuredPost.value))} min read</p>`);
        _push(ssrRenderComponent(_component_router_link, {
          to: `/blog/${featuredPost.value.slug}`,
          class: "read-link mt-auto"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`Read essay`);
            } else {
              return [
                createTextVNode("Read essay")
              ];
            }
          }),
          _: 1
          /* STABLE */
        }, _parent));
        _push(`</div></div></article><section class="latest" data-v-57fed79a><h3 class="mb-2" data-v-57fed79a>Latest</h3><!--[-->`);
        ssrRenderList(remainingPosts.value, (post) => {
          _push(`<article class="story-row row g-3 py-3" data-v-57fed79a><div class="col-12 col-md-4 col-lg-3" data-v-57fed79a><div class="story-thumb" data-v-57fed79a>`);
          if (storyImage(post)) {
            _push(`<img${ssrRenderAttr("src", storyImage(post))}${ssrRenderAttr("alt", post.title)} data-v-57fed79a>`);
          } else {
            _push(`<div class="media-fallback" data-v-57fed79a></div>`);
          }
          _push(`</div></div><div class="col-12 col-md-8 col-lg-9" data-v-57fed79a><div class="story-copy" data-v-57fed79a><p class="type mb-1" data-v-57fed79a>${ssrInterpolate(primaryTag(post))}</p><h4 class="mb-2" data-v-57fed79a>${ssrInterpolate(post.title)}</h4><p class="excerpt mb-2" data-v-57fed79a>${ssrInterpolate(post.excerpt)}</p><p class="meta mb-2" data-v-57fed79a>${ssrInterpolate(formatDate(post.published_at))} · ${ssrInterpolate(readTime(post))} min read</p>`);
          _push(ssrRenderComponent(_component_router_link, {
            to: `/blog/${post.slug}`,
            class: "read-link"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(`Read essay`);
              } else {
                return [
                  createTextVNode("Read essay")
                ];
              }
            }),
            _: 2
            /* DYNAMIC */
          }, _parent));
          _push(`</div></div></article>`);
        });
        _push(`<!--]--></section></div>`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$d = _sfc_main$d.setup;
_sfc_main$d.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/blog/BlogList.vue");
  return _sfc_setup$d ? _sfc_setup$d(props, ctx) : void 0;
};
const BlogList = /* @__PURE__ */ _export_sfc(_sfc_main$d, [["__scopeId", "data-v-57fed79a"]]);
const github = "";
const DEFAULT_VOICE_ID = "default";
let synth = null;
let isPlaying = false;
let playbackStartedAt = 0;
let currentCharIndex = 0;
let currentTextLength = 0;
let progressOffsetChars = 0;
let progressTotalChars = 0;
let estimatedDuration = null;
let voiceObjects = [];
const AVAILABLE_VOICES = [];
function canUseNativeTTS() {
  return typeof window !== "undefined" && typeof window.speechSynthesis !== "undefined" && typeof window.SpeechSynthesisUtterance !== "undefined";
}
function toVoiceId(voice) {
  return (voice == null ? void 0 : voice.voiceURI) || `${(voice == null ? void 0 : voice.name) || "voice"}-${(voice == null ? void 0 : voice.lang) || "unknown"}`;
}
function toVoiceOption(voice) {
  return {
    id: toVoiceId(voice),
    name: `${voice.name} (${voice.lang})`,
    gender: "Unknown",
    accent: voice.lang
  };
}
function refreshVoiceCache() {
  if (!synth)
    return;
  const voices = synth.getVoices() || [];
  voiceObjects = voices;
  const mapped = voices.map(toVoiceOption);
  AVAILABLE_VOICES.splice(0, AVAILABLE_VOICES.length, ...mapped);
  if (!AVAILABLE_VOICES.length) {
    AVAILABLE_VOICES.push({
      id: DEFAULT_VOICE_ID,
      name: "System Default",
      gender: "Unknown",
      accent: "auto"
    });
  }
}
async function waitForVoices(timeoutMs = 1500) {
  if (!synth)
    return;
  refreshVoiceCache();
  if (voiceObjects.length > 0)
    return;
  await new Promise((resolve) => {
    let settled = false;
    const done = () => {
      if (settled)
        return;
      settled = true;
      synth.removeEventListener("voiceschanged", onVoicesChanged);
      resolve();
    };
    const onVoicesChanged = () => {
      refreshVoiceCache();
      done();
    };
    synth.addEventListener("voiceschanged", onVoicesChanged, { once: true });
    setTimeout(done, timeoutMs);
  });
  refreshVoiceCache();
}
function finalizePlayback() {
  isPlaying = false;
  playbackStartedAt = 0;
  currentCharIndex = 0;
  currentTextLength = 0;
  progressOffsetChars = 0;
  progressTotalChars = 0;
}
function getRelativeSpokenChars() {
  if (currentTextLength <= 0)
    return 0;
  let spokenByBoundary = Math.max(0, Math.min(currentTextLength, currentCharIndex));
  if (isPlaying && playbackStartedAt > 0 && typeof estimatedDuration === "number" && estimatedDuration > 0) {
    const elapsedSec = Math.max(0, (performance.now() - playbackStartedAt) / 1e3);
    const ratio = Math.max(0, Math.min(1, elapsedSec / estimatedDuration));
    const spokenByTime = Math.floor(currentTextLength * ratio);
    spokenByBoundary = Math.max(spokenByBoundary, spokenByTime);
  }
  return spokenByBoundary;
}
async function initKokoroTTS(progressCallback = null) {
  if (!canUseNativeTTS()) {
    throw new Error("Browser-native speech synthesis is not supported in this browser.");
  }
  synth = window.speechSynthesis;
  if (progressCallback)
    progressCallback(10);
  await waitForVoices();
  if (progressCallback)
    progressCallback(100);
  return {
    tts: "browser-native",
    device: "browser-native",
    dtype: "n/a"
  };
}
function stopAudio() {
  if (!synth)
    return;
  synth.cancel();
  finalizePlayback();
}
function getPlaybackProgress() {
  if (!isPlaying || progressTotalChars <= 0)
    return 0;
  const absoluteChars = Math.max(0, Math.min(progressTotalChars, progressOffsetChars + getRelativeSpokenChars()));
  const ratio = absoluteChars / progressTotalChars;
  return Math.max(0, Math.min(100, ratio * 100));
}
function getDeviceType() {
  return "browser-native";
}
function cleanup() {
  stopAudio();
  estimatedDuration = null;
}
const noopStorage = {
  getItem() {
    return null;
  },
  setItem() {
  },
  removeItem() {
  }
};
const browserStorage = typeof window !== "undefined" ? window.localStorage : noopStorage;
const useTTSStore = defineStore("tts", {
  state: () => ({
    isInitialized: false,
    isPlaying: false,
    selectedVoice: "default",
    playbackSpeed: 1,
    deviceType: null,
    isLoading: false,
    loadProgress: 0,
    audioDuration: null,
    playbackProgress: 0
  }),
  getters: {
    currentVoice: (state) => {
      return AVAILABLE_VOICES.find((v) => v.id === state.selectedVoice);
    },
    voices: () => AVAILABLE_VOICES
  },
  actions: {
    async initialize(progressCallback = null) {
      if (this.isInitialized)
        return;
      this.isLoading = true;
      this.loadProgress = 0;
      try {
        await initKokoroTTS((progress) => {
          this.loadProgress = progress;
          if (progressCallback) {
            progressCallback(progress);
          }
        });
        this.isInitialized = true;
        this.deviceType = getDeviceType();
      } catch (error) {
        console.error("TTS initialization failed:", error);
        this.isInitialized = false;
        this.deviceType = null;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    stop() {
      stopAudio();
      this.isPlaying = false;
    },
    setVoice(voiceId) {
      this.selectedVoice = voiceId;
      browserStorage.setItem("tts_voice", voiceId);
    },
    setSpeed(speed) {
      this.playbackSpeed = Math.max(0.5, Math.min(2, speed));
      browserStorage.setItem("tts_speed", speed);
    },
    setAudioDuration(duration) {
      this.audioDuration = duration;
    },
    setPlaybackProgress(progress) {
      this.playbackProgress = progress;
    },
    cleanup() {
      cleanup();
      this.isPlaying = false;
      this.isInitialized = false;
      this.selectedVoice = "default";
      this.playbackSpeed = 1;
      this.deviceType = null;
      this.audioDuration = null;
      this.playbackProgress = 0;
    },
    getVoices() {
      return AVAILABLE_VOICES;
    }
  },
  // Restore state on page refresh
  persist: {
    key: "quortol-tts-store",
    storage: browserStorage,
    paths: ["selectedVoice", "playbackSpeed"]
  }
});
const BlogTTS_vue_vue_type_style_index_0_scoped_b2b30eee_lang = "";
const _sfc_main$c = {
  __name: "BlogTTS",
  __ssrInlineRender: true,
  props: {
    content: {
      type: String,
      required: true
    },
    audioUrl: {
      type: String,
      default: null
    },
    isInitialized: {
      type: Boolean,
      default: false
    }
  },
  emits: ["playback-start", "playback-state"],
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const store = useTTSStore();
    const isReady = ref(false);
    const hasError = ref(false);
    const selectedVoice = ref("default");
    const playbackSpeed = ref(1);
    const isSynthesizing = ref(false);
    const recordedAudio = ref(null);
    const recordedIsPlaying = ref(false);
    const recordedCurrentTime = ref(0);
    const recordedDuration = ref(0);
    const recordedError = ref(false);
    let progressFrameId = null;
    const availableVoices = computed(() => store.getVoices());
    const hasRecordedAudio = computed(() => Boolean(props.audioUrl));
    const isPlaying2 = computed(() => hasRecordedAudio.value ? recordedIsPlaying.value : store.isPlaying);
    const formattedProgress = computed(() => {
      if (!store.audioDuration || store.playbackProgress <= 0)
        return "";
      const duration = store.audioDuration;
      const current = store.playbackProgress / 100 * duration;
      const minutes = Math.floor(current / 60);
      const seconds = Math.floor(current % 60);
      const totalMinutes = Math.floor(duration / 60);
      const totalSeconds = Math.floor(duration % 60);
      return `${minutes}:${seconds.toString().padStart(2, "0")} / ${totalMinutes}:${totalSeconds.toString().padStart(2, "0")}`;
    });
    const durationDisplay = computed(() => {
      if (!store.audioDuration)
        return "";
      const minutes = Math.floor(store.audioDuration / 60);
      const seconds = Math.floor(store.audioDuration % 60);
      return `Duration: ${minutes}m ${seconds}s`;
    });
    const playbackProgress = computed(() => {
      if (hasRecordedAudio.value) {
        return recordedDuration.value > 0 ? recordedCurrentTime.value / recordedDuration.value * 100 : 0;
      }
      return store.playbackProgress;
    });
    const formatAudioTime = (seconds) => {
      if (!Number.isFinite(seconds))
        return "0:00";
      const minutes = Math.floor(seconds / 60);
      const remainder = Math.floor(seconds % 60);
      return `${minutes}:${remainder.toString().padStart(2, "0")}`;
    };
    const recordedTimeDisplay = computed(() => {
      if (!recordedDuration.value)
        return "";
      return `${formatAudioTime(recordedCurrentTime.value)} / ${formatAudioTime(recordedDuration.value)}`;
    });
    const stopRecordedAudio = (resetProgress = false) => {
      const audio = recordedAudio.value;
      if (audio) {
        audio.pause();
        if (resetProgress)
          audio.currentTime = 0;
      }
      recordedIsPlaying.value = false;
      if (resetProgress)
        recordedCurrentTime.value = 0;
    };
    const stopProgressPolling = () => {
      if (progressFrameId !== null) {
        cancelAnimationFrame(progressFrameId);
        progressFrameId = null;
      }
    };
    const stopPlaybackSession = (resetProgress = false) => {
      stopAudio();
      stopProgressPolling();
      store.stop();
      if (resetProgress) {
        store.setPlaybackProgress(0);
      }
    };
    const updateProgress = () => {
      if (store.isPlaying) {
        store.setPlaybackProgress(Math.max(store.playbackProgress, getPlaybackProgress()));
      }
    };
    const pollProgress = () => {
      if (progressFrameId !== null)
        return;
      const tick = () => {
        updateProgress();
        if (store.isPlaying) {
          progressFrameId = requestAnimationFrame(tick);
        } else {
          progressFrameId = null;
        }
      };
      progressFrameId = requestAnimationFrame(tick);
    };
    const cleanupTTS = () => {
      stopPlaybackSession();
      store.cleanup();
    };
    const cleanupPlayback = () => {
      stopRecordedAudio();
      if (!hasRecordedAudio.value)
        cleanupTTS();
    };
    onMounted(async () => {
      const savedVoice = typeof window !== "undefined" ? localStorage.getItem("tts_voice") : null;
      const savedSpeed = typeof window !== "undefined" ? localStorage.getItem("tts_speed") : null;
      if (savedVoice && availableVoices.value.some((v) => v.id === savedVoice)) {
        selectedVoice.value = savedVoice;
      }
      if (savedSpeed) {
        playbackSpeed.value = parseFloat(savedSpeed);
      }
      isReady.value = true;
      if (store.isPlaying) {
        pollProgress();
      }
    });
    onUnmounted(() => {
      cleanupPlayback();
    });
    watch(() => props.content, () => {
      if (hasRecordedAudio.value)
        stopRecordedAudio(true);
      else
        stopPlaybackSession();
      store.setAudioDuration(null);
    });
    watch(() => props.audioUrl, () => {
      stopRecordedAudio(true);
      stopPlaybackSession(true);
      recordedDuration.value = 0;
      recordedError.value = false;
    });
    watch(isPlaying2, (playing) => {
      emit("playback-state", playing);
    });
    const stop = () => {
      stopRecordedAudio();
      stopPlaybackSession();
      isSynthesizing.value = false;
    };
    __expose({ stop });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: ["blog-tts-controls", { "loading": !hasRecordedAudio.value && unref(store).isLoading }]
      }, _attrs))} data-v-b2b30eee>`);
      if (hasRecordedAudio.value) {
        _push(`<audio${ssrRenderAttr("src", __props.audioUrl)} preload="metadata" data-v-b2b30eee></audio>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="audio-mode-label" data-v-b2b30eee>${ssrInterpolate(hasRecordedAudio.value ? "Audiobook" : "Text-to-speech")}</div><div class="controls-header" data-v-b2b30eee><button class="play-button"${ssrRenderAttr("aria-label", isPlaying2.value ? "Pause audio" : "Play audio")}${ssrIncludeBooleanAttr(!isReady.value) ? " disabled" : ""} data-v-b2b30eee>`);
      if (!isPlaying2.value) {
        _push(`<span data-v-b2b30eee><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" data-v-b2b30eee><path d="M8 5v14l11-7z" data-v-b2b30eee></path></svg></span>`);
      } else {
        _push(`<span data-v-b2b30eee><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" data-v-b2b30eee><rect x="6" y="6" width="12" height="12" data-v-b2b30eee></rect></svg></span>`);
      }
      _push(`</button>`);
      if (!hasRecordedAudio.value) {
        _push(`<div class="voice-select" data-v-b2b30eee><select${ssrIncludeBooleanAttr(!isReady.value || !unref(store).isInitialized || isSynthesizing.value) ? " disabled" : ""} aria-label="Select voice" data-v-b2b30eee><!--[-->`);
        ssrRenderList(availableVoices.value, (voice) => {
          _push(`<option${ssrRenderAttr("value", voice.id)} data-v-b2b30eee${ssrIncludeBooleanAttr(Array.isArray(selectedVoice.value) ? ssrLooseContain(selectedVoice.value, voice.id) : ssrLooseEqual(selectedVoice.value, voice.id)) ? " selected" : ""}>${ssrInterpolate(voice.name)}</option>`);
        });
        _push(`<!--]--></select></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="speed-control" data-v-b2b30eee><label for="speed-slider" class="sr-only" data-v-b2b30eee>Playback speed</label><input type="range" id="speed-slider" min="0.5" max="2" step="0.1"${ssrRenderAttr("value", playbackSpeed.value)}${ssrIncludeBooleanAttr(!isReady.value || !hasRecordedAudio.value && (!unref(store).isInitialized || isSynthesizing.value)) ? " disabled" : ""} aria-label="Adjust playback speed" data-v-b2b30eee><span class="speed-value" data-v-b2b30eee>${ssrInterpolate(playbackSpeed.value)}x</span></div></div>`);
      if (hasRecordedAudio.value) {
        _push(`<input class="seek-control" type="range" min="0"${ssrRenderAttr("max", recordedDuration.value || 0)} step="0.1"${ssrRenderAttr("value", recordedCurrentTime.value)} aria-label="Seek audiobook" data-v-b2b30eee>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="status-bar" data-v-b2b30eee><div class="status-message" data-v-b2b30eee>`);
      if (hasRecordedAudio.value) {
        _push(`<!--[-->`);
        if (recordedError.value) {
          _push(`<span data-v-b2b30eee>Audiobook unavailable</span>`);
        } else if (recordedIsPlaying.value) {
          _push(`<span class="playing" data-v-b2b30eee>Playing... ${ssrInterpolate(recordedTimeDisplay.value)}</span>`);
        } else {
          _push(`<span data-v-b2b30eee>${ssrInterpolate(recordedTimeDisplay.value || "Loading audiobook...")}</span>`);
        }
        _push(`<!--]-->`);
      } else if (!unref(store).isInitialized) {
        _push(`<!--[-->`);
        if (unref(store).isLoading) {
          _push(`<span class="loading-indicator" data-v-b2b30eee> Loading TTS model... <span class="progress" data-v-b2b30eee>(${ssrInterpolate(unref(store).loadProgress)}%)</span></span>`);
        } else if (!unref(store).isInitialized && hasError.value) {
          _push(`<span data-v-b2b30eee> TTS unavailable </span>`);
        } else {
          _push(`<span data-v-b2b30eee> Ready to read </span>`);
        }
        _push(`<!--]-->`);
      } else if (unref(store).isPlaying) {
        _push(`<span class="playing" data-v-b2b30eee>Playing... ${ssrInterpolate(formattedProgress.value)}</span>`);
      } else {
        _push(`<!--[-->`);
        if (unref(store).audioDuration) {
          _push(`<span data-v-b2b30eee>${ssrInterpolate(durationDisplay.value)}</span>`);
        } else {
          _push(`<span data-v-b2b30eee>Click play to start</span>`);
        }
        _push(`<!--]-->`);
      }
      _push(`</div></div>`);
      if (isPlaying2.value) {
        _push(`<div class="progress-bar" data-v-b2b30eee><div class="progress-fill" style="${ssrRenderStyle({ width: `${playbackProgress.value}%` })}" data-v-b2b30eee></div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$c = _sfc_main$c.setup;
_sfc_main$c.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/components/blog/BlogTTS.vue");
  return _sfc_setup$c ? _sfc_setup$c(props, ctx) : void 0;
};
const BlogTTS = /* @__PURE__ */ _export_sfc(_sfc_main$c, [["__scopeId", "data-v-b2b30eee"]]);
const BlogRSVP_vue_vue_type_style_index_0_scoped_4bbd4478_lang = "";
const STORAGE_KEY = "quortol-rsvp-wpm";
const DEFAULT_WPM = 300;
const MIN_WPM = 100;
const MAX_WPM = 1e3;
const WPM_STEP = 50;
const _sfc_main$b = {
  __name: "BlogRSVP",
  __ssrInlineRender: true,
  props: {
    content: {
      type: String,
      required: true
    }
  },
  emits: ["playback-start", "playback-state"],
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const tokenize = (content) => (content || "").trim().split(/\s+/).filter(Boolean);
    const words = computed(() => tokenize(props.content));
    const wordIndex = ref(0);
    const isPlaying2 = ref(false);
    const hasFinished = ref(false);
    const wpm = ref(DEFAULT_WPM);
    const speeds = Array.from(
      { length: (MAX_WPM - MIN_WPM) / WPM_STEP + 1 },
      (_, index) => MIN_WPM + index * WPM_STEP
    );
    const lastIndex = computed(() => Math.max(0, words.value.length - 1));
    const currentWord = computed(() => words.value[wordIndex.value] || "Ready");
    const positionLabel = computed(() => words.value.length ? `Word ${wordIndex.value + 1} of ${words.value.length}` : "No words available");
    const elapsedSeconds = computed(() => wordIndex.value * 60 / wpm.value);
    const totalSeconds = computed(() => words.value.length * 60 / wpm.value);
    const formatTime = (seconds) => {
      const safeSeconds = Math.max(0, Math.round(seconds));
      const minutes = Math.floor(safeSeconds / 60);
      return `${minutes}:${String(safeSeconds % 60).padStart(2, "0")}`;
    };
    const elapsedDisplay = computed(() => formatTime(elapsedSeconds.value));
    const totalDisplay = computed(() => formatTime(totalSeconds.value));
    const setPlaying = (value) => {
      if (isPlaying2.value === value)
        return;
      isPlaying2.value = value;
      emit("playback-state", value);
    };
    const pause = () => {
      setPlaying(false);
    };
    const restoreSpeed = () => {
      if (typeof window === "undefined")
        return;
      try {
        const saved = Number(window.localStorage.getItem(STORAGE_KEY));
        if (saved >= MIN_WPM && saved <= MAX_WPM && saved % WPM_STEP === 0) {
          wpm.value = saved;
        }
      } catch {
        wpm.value = DEFAULT_WPM;
      }
    };
    const stop = () => pause();
    watch(() => props.content, () => {
      pause();
      wordIndex.value = 0;
      hasFinished.value = false;
    });
    onMounted(restoreSpeed);
    onUnmounted(pause);
    __expose({ stop });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({
        class: "blog-rsvp",
        "aria-labelledby": "rsvp-heading"
      }, _attrs))} data-v-4bbd4478><div class="rsvp-heading-row" data-v-4bbd4478><div data-v-4bbd4478><p class="rsvp-kicker" data-v-4bbd4478>Speed reader</p><h2 id="rsvp-heading" data-v-4bbd4478>Rapid Serial Visual Presentation</h2></div><span class="rsvp-time" data-v-4bbd4478>${ssrInterpolate(elapsedDisplay.value)} / ${ssrInterpolate(totalDisplay.value)}</span></div><div class="word-stage" aria-live="off" aria-label="RSVP word display" data-v-4bbd4478><span class="word" data-v-4bbd4478>${ssrInterpolate(currentWord.value)}</span></div><label class="sr-only" for="rsvp-position" data-v-4bbd4478>Reading position</label><input id="rsvp-position" class="position-slider" type="range" min="0"${ssrRenderAttr("max", lastIndex.value)}${ssrRenderAttr("value", wordIndex.value)}${ssrRenderAttr("aria-valuetext", positionLabel.value)} data-v-4bbd4478><div class="position-label" aria-hidden="true" data-v-4bbd4478>${ssrInterpolate(positionLabel.value)}</div><div class="rsvp-controls" data-v-4bbd4478><button type="button" class="rsvp-play"${ssrIncludeBooleanAttr(!words.value.length) ? " disabled" : ""} data-v-4bbd4478>${ssrInterpolate(isPlaying2.value ? "Pause" : hasFinished.value ? "Read again" : "Start RSVP")}</button><button type="button"${ssrIncludeBooleanAttr(!words.value.length || wordIndex.value === 0) ? " disabled" : ""} data-v-4bbd4478>Restart</button><label for="rsvp-speed" data-v-4bbd4478>Speed</label><select id="rsvp-speed"${ssrRenderAttr("value", wpm.value)} data-v-4bbd4478><!--[-->`);
      ssrRenderList(unref(speeds), (speed) => {
        _push(`<option${ssrRenderAttr("value", speed)} data-v-4bbd4478>${ssrInterpolate(speed)} WPM</option>`);
      });
      _push(`<!--]--></select></div></section>`);
    };
  }
};
const _sfc_setup$b = _sfc_main$b.setup;
_sfc_main$b.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/components/blog/BlogRSVP.vue");
  return _sfc_setup$b ? _sfc_setup$b(props, ctx) : void 0;
};
const BlogRSVP = /* @__PURE__ */ _export_sfc(_sfc_main$b, [["__scopeId", "data-v-4bbd4478"]]);
const BlogDetail_vue_vue_type_style_index_0_scoped_a6533fe0_lang = "";
const _sfc_main$a = {
  __name: "BlogDetail",
  __ssrInlineRender: true,
  setup(__props) {
    var _a;
    const route = useRoute();
    const prerenderRouteData = usePrerenderRouteData();
    const post = ref(((_a = prerenderRouteData.value) == null ? void 0 : _a.post) || null);
    const loading = ref(!post.value);
    const store = useTTSStore();
    const contentRef = ref(null);
    const fullscreenImage = ref(null);
    const ttsRef = ref(null);
    const rsvpRef = ref(null);
    const handleTTSStart = () => {
      var _a2;
      (_a2 = rsvpRef.value) == null ? void 0 : _a2.stop();
    };
    const handleRSVPStart = () => {
      var _a2;
      (_a2 = ttsRef.value) == null ? void 0 : _a2.stop();
    };
    const slug = computed(() => route.params.slug);
    const markdownParser = new MarkdownIt({
      html: true,
      linkify: true,
      typographer: true,
      highlight: (str, lang) => {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`;
          } catch (error) {
            console.warn("Code highlight failed:", error);
          }
        }
        return `<pre class="hljs"><code>${markdownParser.utils.escapeHtml(str)}</code></pre>`;
      }
    });
    const defaultLinkRenderer = markdownParser.renderer.rules.link_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
    markdownParser.renderer.rules.link_open = (tokens, idx, options, env, self) => {
      const href = tokens[idx].attrGet("href");
      if (href && /^(https?:)?\/\//.test(href)) {
        tokens[idx].attrSet("target", "_blank");
        tokens[idx].attrSet("rel", "noopener noreferrer");
      }
      return defaultLinkRenderer(tokens, idx, options, env, self);
    };
    const applyPostSEO = (postData) => {
      if (!postData)
        return;
      applySEOMetadata({
        title: `${postData.title} | Quortol`,
        description: buildDescription(postData.excerpt || postData.content || ""),
        path: `/blog/${postData.slug}`,
        ogType: "article",
        ogImage: postData.featured_image || "",
        structuredData: [buildBlogPostingStructuredData(postData)]
      });
    };
    const loadPost = async (targetSlug) => {
      var _a2;
      if (((_a2 = post.value) == null ? void 0 : _a2.slug) === targetSlug) {
        loading.value = false;
        if (typeof document !== "undefined") {
          applyPostSEO(post.value);
        }
        return;
      }
      loading.value = true;
      try {
        const response = await blog.getPost(targetSlug);
        post.value = response.data;
        applyPostSEO(post.value);
      } catch (error) {
        console.error("Error loading post:", error);
        post.value = null;
        applySEOMetadata({
          title: "Post Not Found | Quortol",
          description: "The requested blog post could not be found.",
          path: `/blog/${targetSlug}`,
          robots: "index,follow"
        });
      } finally {
        loading.value = false;
      }
    };
    const closeImageViewer = () => {
      fullscreenImage.value = null;
    };
    const decorateInlineImages = async () => {
      await nextTick();
      if (!contentRef.value)
        return;
      const images = contentRef.value.querySelectorAll("img");
      images.forEach((image) => {
        var _a2;
        image.classList.add("clickable-image");
        image.setAttribute("tabindex", "0");
        image.setAttribute("role", "button");
        if (!image.getAttribute("aria-label")) {
          const alt = image.getAttribute("alt") || ((_a2 = post.value) == null ? void 0 : _a2.title) || "Open image in fullscreen";
          image.setAttribute("aria-label", `Open image: ${alt}`);
        }
      });
    };
    const handleGlobalKeydown = (event) => {
      if (event.key === "Escape" && fullscreenImage.value) {
        closeImageViewer();
      }
    };
    watch(
      () => slug.value,
      (nextSlug) => {
        if (nextSlug) {
          loadPost(nextSlug);
        }
      },
      { immediate: true }
    );
    watch(
      () => post.value,
      (nextPost) => {
        if (nextPost && typeof document !== "undefined") {
          applyPostSEO(nextPost);
        }
      },
      { immediate: true }
    );
    onUnmounted(() => {
      store.stop();
      store.cleanup();
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleGlobalKeydown);
    });
    onMounted(() => {
      window.addEventListener("keydown", handleGlobalKeydown);
    });
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric"
      });
    };
    const sourceContent = computed(() => {
      var _a2;
      return ((_a2 = post.value) == null ? void 0 : _a2.content) || "";
    });
    const heroImageUrl = computed(() => {
      var _a2;
      return extractHeroImage({
        content: sourceContent.value,
        featuredImage: ((_a2 = post.value) == null ? void 0 : _a2.featured_image) || ""
      });
    });
    const displayContent = computed(() => {
      var _a2;
      return sanitizeBlogDisplayContent({
        content: sourceContent.value,
        title: ((_a2 = post.value) == null ? void 0 : _a2.title) || "",
        featuredImage: heroImageUrl.value
      });
    });
    const plainTextContent = computed(() => {
      return extractPlainTextFromMarkdown(displayContent.value);
    });
    const wordCount = computed(() => {
      if (!plainTextContent.value)
        return 0;
      return plainTextContent.value.split(/\s+/).length;
    });
    const readTime = computed(() => {
      return Math.max(1, Math.round(wordCount.value / 220));
    });
    const dek = computed(() => {
      var _a2, _b;
      const excerpt = (_b = (_a2 = post.value) == null ? void 0 : _a2.excerpt) == null ? void 0 : _b.trim();
      if (excerpt)
        return excerpt;
      if (!plainTextContent.value)
        return "";
      return `${plainTextContent.value.slice(0, 220).trim()}...`;
    });
    const renderedContent = computed(() => {
      if (!displayContent.value)
        return "";
      return markdownParser.render(displayContent.value).replace("<p>", '<p class="lead-paragraph">');
    });
    watch(renderedContent, () => {
      decorateInlineImages();
    });
    watch(fullscreenImage, (imageState) => {
      document.body.style.overflow = imageState ? "hidden" : "";
    });
    return (_ctx, _push, _parent, _attrs) => {
      var _a2, _b;
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "essay-page" }, _attrs))} data-v-a6533fe0>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/blog",
        class: "back-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`← Back to Essays`);
          } else {
            return [
              createTextVNode("← Back to Essays")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      if (loading.value) {
        _push(`<div class="loading" data-v-a6533fe0>Loading post...</div>`);
      } else if (post.value) {
        _push(`<article class="essay" data-v-a6533fe0><header class="hero" data-v-a6533fe0>`);
        if (heroImageUrl.value) {
          _push(`<figure class="hero-image" data-v-a6533fe0><img${ssrRenderAttr("src", heroImageUrl.value)}${ssrRenderAttr("alt", post.value.title)} class="clickable-image" tabindex="0" role="button" data-v-a6533fe0></figure>`);
        } else {
          _push(`<div class="hero-fallback" data-v-a6533fe0></div>`);
        }
        if ((_a2 = post.value.tags) == null ? void 0 : _a2.length) {
          _push(`<p class="kicker" data-v-a6533fe0>${ssrInterpolate(post.value.tags[0].name)}</p>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<h1 class="title" data-v-a6533fe0>${ssrInterpolate(post.value.title)}</h1><p class="dek" data-v-a6533fe0>${ssrInterpolate(dek.value)}</p><div class="meta-row" data-v-a6533fe0><span data-v-a6533fe0>${ssrInterpolate(formatDate(post.value.published_at))}</span><span data-v-a6533fe0>${ssrInterpolate(readTime.value)} min read</span><span data-v-a6533fe0>${ssrInterpolate(wordCount.value.toLocaleString())} words</span></div>`);
        if ((_b = post.value.tags) == null ? void 0 : _b.length) {
          _push(`<div class="tag-row" data-v-a6533fe0><!--[-->`);
          ssrRenderList(post.value.tags, (tag) => {
            _push(`<span class="tag" data-v-a6533fe0>${ssrInterpolate(tag.name)}</span>`);
          });
          _push(`<!--]--></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</header>`);
        if (plainTextContent.value) {
          _push(ssrRenderComponent(BlogTTS, {
            ref_key: "ttsRef",
            ref: ttsRef,
            content: plainTextContent.value,
            "audio-url": post.value.audio_url,
            "is-initialized": unref(store).isInitialized,
            onPlaybackStart: handleTTSStart
          }, null, _parent));
        } else {
          _push(`<!---->`);
        }
        if (plainTextContent.value) {
          _push(ssrRenderComponent(BlogRSVP, {
            ref_key: "rsvpRef",
            ref: rsvpRef,
            content: plainTextContent.value,
            onPlaybackStart: handleRSVPStart
          }, null, _parent));
        } else {
          _push(`<!---->`);
        }
        _push(`<section class="content" data-v-a6533fe0>${renderedContent.value ?? ""}</section></article>`);
      } else {
        _push(`<div class="not-found" data-v-a6533fe0>Post not found</div>`);
      }
      if (fullscreenImage.value) {
        _push(`<div class="image-lightbox" role="dialog" aria-modal="true" aria-label="Image viewer" data-v-a6533fe0><button class="lightbox-close" type="button" aria-label="Close image viewer" data-v-a6533fe0> Close </button><img${ssrRenderAttr("src", fullscreenImage.value.src)}${ssrRenderAttr("alt", fullscreenImage.value.alt)} class="lightbox-image" data-v-a6533fe0></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$a = _sfc_main$a.setup;
_sfc_main$a.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/blog/BlogDetail.vue");
  return _sfc_setup$a ? _sfc_setup$a(props, ctx) : void 0;
};
const BlogDetail = /* @__PURE__ */ _export_sfc(_sfc_main$a, [["__scopeId", "data-v-a6533fe0"]]);
const PodcastList_vue_vue_type_style_index_0_scoped_356bc522_lang = "";
const defaultImage = "/quortol-podcast-cover.svg";
const _sfc_main$9 = {
  __name: "PodcastList",
  __ssrInlineRender: true,
  setup(__props) {
    var _a;
    const prerenderRouteData = usePrerenderRouteData();
    const episodes = ref(((_a = prerenderRouteData.value) == null ? void 0 : _a.podcasts) || []);
    const loading = ref(episodes.value.length === 0);
    const featuredEpisode = computed(() => episodes.value[0] || null);
    const remainingEpisodes = computed(() => episodes.value.slice(1));
    const formatDate = (date) => new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
    const sourceLabel = (episode) => episode.source_type === "blog" ? "Essay Adaptation" : "Podcast";
    onMounted(async () => {
      if (episodes.value.length > 0) {
        loading.value = false;
        return;
      }
      try {
        const response = await podcast.getEpisodes();
        episodes.value = response.data.podcasts || [];
      } catch (error) {
        console.error("Error loading podcasts:", error);
      } finally {
        loading.value = false;
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "podcast-index container-xl py-4 py-md-5" }, _attrs))} data-v-356bc522><header class="masthead mb-4" data-v-356bc522><p class="brand mb-2" data-v-356bc522>Listen</p><h1 class="display-4 mb-2" data-v-356bc522>Podcasts</h1><p class="deck mb-0" data-v-356bc522> Audio conversations adapted from Quortol essays and original podcast episodes. </p></header>`);
      if (loading.value) {
        _push(`<div class="text-center text-muted py-4" data-v-356bc522>Loading podcasts...</div>`);
      } else if (episodes.value.length === 0) {
        _push(`<div class="text-center text-muted py-4" data-v-356bc522> No podcast episodes published yet. </div>`);
      } else {
        _push(`<div class="index-content" data-v-356bc522><article class="featured row g-3 g-lg-4 pb-4 mb-4" data-v-356bc522><div class="col-12 col-lg-7" data-v-356bc522><div class="featured-media h-100" data-v-356bc522><img${ssrRenderAttr("src", featuredEpisode.value.image_url || defaultImage)}${ssrRenderAttr("alt", featuredEpisode.value.title)} data-v-356bc522></div></div><div class="col-12 col-lg-5" data-v-356bc522><div class="featured-copy h-100 d-flex flex-column" data-v-356bc522><p class="type mb-2" data-v-356bc522>${ssrInterpolate(sourceLabel(featuredEpisode.value))}</p><h2 class="mb-2" data-v-356bc522>${ssrInterpolate(featuredEpisode.value.title)}</h2><p class="excerpt mb-2" data-v-356bc522>${ssrInterpolate(featuredEpisode.value.summary)}</p><p class="meta mb-2" data-v-356bc522>${ssrInterpolate(formatDate(featuredEpisode.value.published_at))}</p>`);
        if (featuredEpisode.value.related_blog_title) {
          _push(`<p class="related mb-3" data-v-356bc522> From essay: ${ssrInterpolate(featuredEpisode.value.related_blog_title)}</p>`);
        } else {
          _push(`<!---->`);
        }
        _push(ssrRenderComponent(_component_router_link, {
          to: `/podcasts/${featuredEpisode.value.slug}`,
          class: "read-link mt-auto"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(` Listen now `);
            } else {
              return [
                createTextVNode(" Listen now ")
              ];
            }
          }),
          _: 1
          /* STABLE */
        }, _parent));
        _push(`</div></div></article><section class="latest" data-v-356bc522><h3 class="mb-2" data-v-356bc522>Latest</h3><!--[-->`);
        ssrRenderList(remainingEpisodes.value, (episode) => {
          _push(`<article class="story-row row g-3 py-3" data-v-356bc522><div class="col-12 col-md-4 col-lg-3" data-v-356bc522><div class="story-thumb" data-v-356bc522><img${ssrRenderAttr("src", episode.image_url || defaultImage)}${ssrRenderAttr("alt", episode.title)} data-v-356bc522></div></div><div class="col-12 col-md-8 col-lg-9" data-v-356bc522><div class="story-copy" data-v-356bc522><p class="type mb-1" data-v-356bc522>${ssrInterpolate(sourceLabel(episode))}</p><h4 class="mb-2" data-v-356bc522>${ssrInterpolate(episode.title)}</h4><p class="excerpt mb-2" data-v-356bc522>${ssrInterpolate(episode.summary)}</p><p class="meta mb-2" data-v-356bc522>${ssrInterpolate(formatDate(episode.published_at))}</p>`);
          if (episode.related_blog_title) {
            _push(`<p class="related mb-2" data-v-356bc522> From essay: ${ssrInterpolate(episode.related_blog_title)}</p>`);
          } else {
            _push(`<!---->`);
          }
          _push(ssrRenderComponent(_component_router_link, {
            to: `/podcasts/${episode.slug}`,
            class: "read-link"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(` Listen now `);
              } else {
                return [
                  createTextVNode(" Listen now ")
                ];
              }
            }),
            _: 2
            /* DYNAMIC */
          }, _parent));
          _push(`</div></div></article>`);
        });
        _push(`<!--]--></section></div>`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$9 = _sfc_main$9.setup;
_sfc_main$9.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/podcasts/PodcastList.vue");
  return _sfc_setup$9 ? _sfc_setup$9(props, ctx) : void 0;
};
const PodcastList = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["__scopeId", "data-v-356bc522"]]);
const PodcastDetail_vue_vue_type_style_index_0_scoped_5bb09e2c_lang = "";
const _sfc_main$8 = {
  __name: "PodcastDetail",
  __ssrInlineRender: true,
  setup(__props) {
    var _a;
    const route = useRoute();
    const prerenderRouteData = usePrerenderRouteData();
    const episode = ref(((_a = prerenderRouteData.value) == null ? void 0 : _a.episode) || null);
    const loading = ref(!episode.value);
    const hasTrackedAudioPlay = ref(false);
    const markdownParser = new MarkdownIt({
      html: true,
      linkify: true,
      typographer: true
    });
    const heroImageUrl = computed(() => {
      var _a2;
      return ((_a2 = episode.value) == null ? void 0 : _a2.image_url) || "/quortol-podcast-cover.svg";
    });
    const renderedTranscript = computed(
      () => {
        var _a2;
        return markdownParser.render(((_a2 = episode.value) == null ? void 0 : _a2.transcript_markdown) || "");
      }
    );
    const applyEpisodeSEO = (episodeData) => {
      if (!episodeData)
        return;
      applySEOMetadata({
        title: `${episodeData.title} | Quortol`,
        description: buildDescription(
          episodeData.summary || episodeData.transcript_markdown || "",
          "Listen to a Quortol podcast episode."
        ),
        path: `/podcasts/${episodeData.slug}`,
        ogType: "article",
        ogImage: episodeData.image_url || "/quortol-podcast-cover.svg",
        structuredData: [buildPodcastEpisodeStructuredData(episodeData)]
      });
    };
    const formatDate = (date) => new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
    const formatDuration = (durationSeconds) => {
      const totalSeconds = Math.max(0, Math.round(Number(durationSeconds) || 0));
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;
      if (minutes <= 0)
        return `${seconds}s`;
      return `${minutes}m ${String(seconds).padStart(2, "0")}s`;
    };
    const loadEpisode = async (slug) => {
      var _a2;
      if (!slug)
        return;
      if (((_a2 = episode.value) == null ? void 0 : _a2.slug) === slug) {
        loading.value = false;
        applyEpisodeSEO(episode.value);
        return;
      }
      loading.value = true;
      try {
        const response = await podcast.getEpisode(slug);
        episode.value = response.data.podcast;
        hasTrackedAudioPlay.value = false;
        applyEpisodeSEO(episode.value);
      } catch (error) {
        console.error("Error loading podcast episode:", error);
        episode.value = null;
        applySEOMetadata({
          title: "Podcast Episode Not Found | Quortol",
          description: "The requested podcast episode could not be found.",
          path: `/podcasts/${slug}`,
          robots: "index,follow"
        });
      } finally {
        loading.value = false;
      }
    };
    watch(
      () => route.params.slug,
      (slug) => {
        loadEpisode(slug);
      },
      { immediate: true }
    );
    watch(
      () => episode.value,
      (nextEpisode) => {
        hasTrackedAudioPlay.value = false;
        if (nextEpisode && typeof document !== "undefined") {
          applyEpisodeSEO(nextEpisode);
        }
      },
      { immediate: true }
    );
    return (_ctx, _push, _parent, _attrs) => {
      var _a2, _b;
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "podcast-page" }, _attrs))} data-v-5bb09e2c>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/podcasts",
        class: "back-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`← Back to Podcasts`);
          } else {
            return [
              createTextVNode("← Back to Podcasts")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      if (loading.value) {
        _push(`<div class="loading" data-v-5bb09e2c>Loading episode...</div>`);
      } else if (episode.value) {
        _push(`<article class="episode" data-v-5bb09e2c><header class="hero" data-v-5bb09e2c><figure class="hero-image" data-v-5bb09e2c><img${ssrRenderAttr("src", heroImageUrl.value)}${ssrRenderAttr("alt", episode.value.title)} data-v-5bb09e2c></figure><p class="kicker" data-v-5bb09e2c>${ssrInterpolate(episode.value.source_type === "blog" ? "Essay Adaptation" : "Podcast")}</p><h1 class="title" data-v-5bb09e2c>${ssrInterpolate(episode.value.title)}</h1><p class="dek" data-v-5bb09e2c>${ssrInterpolate(episode.value.summary)}</p><div class="meta-row" data-v-5bb09e2c><span data-v-5bb09e2c>${ssrInterpolate(formatDate(episode.value.published_at))}</span>`);
        if ((_a2 = episode.value.audio_meta) == null ? void 0 : _a2.duration_seconds) {
          _push(`<span data-v-5bb09e2c>${ssrInterpolate(formatDuration(episode.value.audio_meta.duration_seconds))}</span>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<span data-v-5bb09e2c>${ssrInterpolate(((_b = episode.value.audio_meta) == null ? void 0 : _b.content_type) || "audio/wav")}</span></div><div class="action-row" data-v-5bb09e2c><a${ssrRenderAttr("href", episode.value.audio_url)} class="listen-link" data-v-5bb09e2c>Open audio file</a>`);
        if (episode.value.related_blog_slug) {
          _push(ssrRenderComponent(_component_router_link, {
            to: `/blog/${episode.value.related_blog_slug}`,
            class: "related-link"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(` Read related essay `);
              } else {
                return [
                  createTextVNode(" Read related essay ")
                ];
              }
            }),
            _: 1
            /* STABLE */
          }, _parent));
        } else {
          _push(`<!---->`);
        }
        _push(`</div></header><section class="player card app-card mb-4" data-v-5bb09e2c><div class="card-body" data-v-5bb09e2c><audio controls preload="none" class="w-100"${ssrRenderAttr("src", episode.value.audio_url)} data-v-5bb09e2c> Your browser does not support audio playback. </audio></div></section><section class="transcript-section" data-v-5bb09e2c><h2 class="section-title" data-v-5bb09e2c>Transcript</h2><div class="transcript content" data-v-5bb09e2c>${renderedTranscript.value ?? ""}</div></section></article>`);
      } else {
        _push(`<div class="not-found" data-v-5bb09e2c>Podcast episode not found.</div>`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$8 = _sfc_main$8.setup;
_sfc_main$8.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/podcasts/PodcastDetail.vue");
  return _sfc_setup$8 ? _sfc_setup$8(props, ctx) : void 0;
};
const PodcastDetail = /* @__PURE__ */ _export_sfc(_sfc_main$8, [["__scopeId", "data-v-5bb09e2c"]]);
const AgentLogin_vue_vue_type_style_index_0_lang = "";
const _sfc_main$7 = {
  __name: "AgentLogin",
  __ssrInlineRender: true,
  setup(__props) {
    useRouter();
    useAuthStore();
    const username = ref("");
    const password = ref("");
    const error = ref("");
    const loading = ref(false);
    const showRegisterForm = ref(false);
    const registrationEnabled = ref(false);
    const registerData = reactive({ username: "", email: "", password: "" });
    const registerError = ref("");
    const registerLoading = ref(false);
    onMounted(async () => {
      var _a;
      try {
        const response = await auth.getSettings();
        registrationEnabled.value = Boolean((_a = response.data) == null ? void 0 : _a.registration_enabled);
      } catch (err) {
        registrationEnabled.value = false;
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "agent-login" }, _attrs))}><div class="login-container"><h1>Agent Access</h1><p class="subtitle">Login to access agent capabilities</p><form class="login-form"><div class="form-group"><label for="username">Username</label><input type="text" id="username"${ssrRenderAttr("value", username.value)} placeholder="Enter your username" required></div><div class="form-group"><label for="password">Password</label><input type="password" id="password"${ssrRenderAttr("value", password.value)} placeholder="Enter your password" required></div>`);
      if (error.value) {
        _push(`<div class="error">${ssrInterpolate(error.value)}</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<button type="submit" class="submit-btn"${ssrIncludeBooleanAttr(loading.value) ? " disabled" : ""}>`);
      if (loading.value) {
        _push(`<span>Logging in...</span>`);
      } else {
        _push(`<span>Login to Agents</span>`);
      }
      _push(`</button>`);
      if (registrationEnabled.value) {
        _push(`<div class="register-link"> New here? <a href="#">Register</a></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</form>`);
      if (registrationEnabled.value && showRegisterForm.value) {
        _push(`<div class="register-form"><h2>Register</h2><form class="login-form"><div class="form-group"><label for="reg-username">Username</label><input type="text" id="reg-username"${ssrRenderAttr("value", registerData.username)} placeholder="Choose a username" required></div><div class="form-group"><label for="reg-email">Email</label><input type="email" id="reg-email"${ssrRenderAttr("value", registerData.email)} placeholder="Enter your email" required></div><div class="form-group"><label for="reg-password">Password</label><input type="password" id="reg-password"${ssrRenderAttr("value", registerData.password)} placeholder="Choose a password" required></div>`);
        if (registerError.value) {
          _push(`<div class="error">${ssrInterpolate(registerError.value)}</div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<button type="submit" class="submit-btn"${ssrIncludeBooleanAttr(registerLoading.value) ? " disabled" : ""}>`);
        if (registerLoading.value) {
          _push(`<span>Creating account...</span>`);
        } else {
          _push(`<span>Register</span>`);
        }
        _push(`</button><div class="login-link"> Already have an account? <a href="#">Login</a></div></form></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div>`);
    };
  }
};
const _sfc_setup$7 = _sfc_main$7.setup;
_sfc_main$7.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/agents/AgentLogin.vue");
  return _sfc_setup$7 ? _sfc_setup$7(props, ctx) : void 0;
};
const AgentDashboard_vue_vue_type_style_index_0_lang = "";
const _sfc_main$6 = {
  __name: "AgentDashboard",
  __ssrInlineRender: true,
  setup(__props) {
    const authStore = useAuthStore();
    const agentList = ref([]);
    const loading = ref(true);
    onMounted(async () => {
      try {
        const response = await agents.getAgents();
        agentList.value = response.data;
      } catch (error) {
        console.error("Error loading agents:", error);
        authStore.logout();
      } finally {
        loading.value = false;
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "agent-dashboard" }, _attrs))}><h1>Agent Dashboard</h1>`);
      if (loading.value) {
        _push(`<div class="loading">Loading agents...</div>`);
      } else {
        _push(`<div class="dashboard-content">`);
        if (agentList.value.length === 0) {
          _push(`<div class="no-agents">No agents available yet.</div>`);
        } else {
          _push(`<div class="agents-grid"><!--[-->`);
          ssrRenderList(agentList.value, (agent) => {
            _push(`<div class="agent-card"><h3>${ssrInterpolate(agent.name)}</h3><p class="description">${ssrInterpolate(agent.description)}</p><div class="status"><span class="${ssrRenderClass(["status-badge", agent.status])}">${ssrInterpolate(agent.status.toUpperCase())}</span></div>`);
            _push(ssrRenderComponent(_component_router_link, {
              to: `/agent/agents/${agent.id}/capabilities`,
              class: "view-capabilities"
            }, {
              default: withCtx((_, _push2, _parent2, _scopeId) => {
                if (_push2) {
                  _push2(` View Capabilities → `);
                } else {
                  return [
                    createTextVNode(" View Capabilities → ")
                  ];
                }
              }),
              _: 2
              /* DYNAMIC */
            }, _parent));
            _push(`</div>`);
          });
          _push(`<!--]--></div>`);
        }
        _push(`</div>`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$6 = _sfc_main$6.setup;
_sfc_main$6.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/agents/AgentDashboard.vue");
  return _sfc_setup$6 ? _sfc_setup$6(props, ctx) : void 0;
};
const AgentCapabilities_vue_vue_type_style_index_0_lang = "";
const _sfc_main$5 = {
  __name: "AgentCapabilities",
  __ssrInlineRender: true,
  setup(__props) {
    const route = useRoute();
    const agent = ref(null);
    const loading = ref(true);
    const error = ref("");
    const successMessage = ref("");
    const response = ref(null);
    const selectedCapability = ref("");
    const paramsInput = ref("");
    const executing = ref(false);
    const agentId = computed(() => route.params.agentId);
    onMounted(async () => {
      try {
        const response2 = await agents.getAgent(agentId.value);
        agent.value = response2.data;
      } catch (err) {
        console.error("Error loading agent:", err);
      } finally {
        loading.value = false;
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      var _a;
      const _component_router_link = resolveComponent("router-link");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "agent-capabilities" }, _attrs))}>`);
      _push(ssrRenderComponent(_component_router_link, {
        to: "/agent/dashboard",
        class: "back-link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`← Back to Agents`);
          } else {
            return [
              createTextVNode("← Back to Agents")
            ];
          }
        }),
        _: 1
        /* STABLE */
      }, _parent));
      if (loading.value) {
        _push(`<div class="loading">Loading agent...</div>`);
      } else if (agent.value) {
        _push(`<div class="capability-content"><h1>${ssrInterpolate(agent.value.name)}</h1><div class="meta"><span>${ssrInterpolate(agent.value.description)}</span><span class="${ssrRenderClass(["status", agent.value.status])}">${ssrInterpolate(agent.value.status.toUpperCase())}</span></div>`);
        if ((_a = agent.value.capabilities) == null ? void 0 : _a.length) {
          _push(`<div class="capabilities-section"><h2>Available Capabilities</h2><div class="capabilities-list"><!--[-->`);
          ssrRenderList(agent.value.capabilities, (cap) => {
            _push(`<div class="capability-item"><span class="capability-name">${ssrInterpolate(cap)}</span></div>`);
          });
          _push(`<!--]--></div></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<div class="execute-section"><h2>Execute Capability</h2><form class="execute-form"><div class="form-group"><label for="capability">Select Capability</label><select required><option value=""${ssrIncludeBooleanAttr(Array.isArray(selectedCapability.value) ? ssrLooseContain(selectedCapability.value, "") : ssrLooseEqual(selectedCapability.value, "")) ? " selected" : ""}>-- Choose a capability --</option><!--[-->`);
        ssrRenderList(agent.value.capabilities, (cap) => {
          _push(`<option${ssrRenderAttr("value", cap)}${ssrIncludeBooleanAttr(Array.isArray(selectedCapability.value) ? ssrLooseContain(selectedCapability.value, cap) : ssrLooseEqual(selectedCapability.value, cap)) ? " selected" : ""}>${ssrInterpolate(cap)}</option>`);
        });
        _push(`<!--]--></select></div><div class="form-group"><label for="params">Parameters (JSON)</label><textarea id="params" placeholder="{&quot;param1&quot;: &quot;value1&quot;, &quot;param2&quot;: &quot;value2&quot;}" rows="4">${ssrInterpolate(paramsInput.value)}</textarea></div>`);
        if (error.value) {
          _push(`<div class="error">${ssrInterpolate(error.value)}</div>`);
        } else {
          _push(`<!---->`);
        }
        if (successMessage.value) {
          _push(`<div class="success">${ssrInterpolate(successMessage.value)}</div>`);
        } else {
          _push(`<!---->`);
        }
        if (response.value) {
          _push(`<div class="response-preview"><h3>Response</h3><pre>${ssrInterpolate(response.value)}</pre></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<button type="submit" class="submit-btn"${ssrIncludeBooleanAttr(executing.value || !selectedCapability.value) ? " disabled" : ""}>`);
        if (executing.value) {
          _push(`<span>Executing...</span>`);
        } else {
          _push(`<span>Execute</span>`);
        }
        _push(`</button></form></div></div>`);
      } else {
        _push(`<div class="not-found">Agent not found</div>`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$5 = _sfc_main$5.setup;
_sfc_main$5.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/agents/AgentCapabilities.vue");
  return _sfc_setup$5 ? _sfc_setup$5(props, ctx) : void 0;
};
const PostCard_vue_vue_type_style_index_0_scoped_cdf3720c_lang = "";
const _sfc_main$4 = {
  __name: "PostCard",
  __ssrInlineRender: true,
  props: {
    post: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ["click", "filter-tag"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const postRef = ref(null);
    ref(null);
    const imageFailed = ref(false);
    const videoFailed = ref(false);
    const hasMediaContent = computed(() => Boolean(props.post.media_url || props.post.video_url));
    const showImage = computed(() => Boolean(props.post.media_url) && !imageFailed.value);
    const showVideo = computed(() => Boolean(props.post.video_url) && !videoFailed.value);
    const formatRelativeTime = () => {
      const timestamp = new Date(props.post.timestamp);
      const now = /* @__PURE__ */ new Date();
      const diffMs = now - timestamp;
      const diffDays = Math.floor(diffMs / (1e3 * 60 * 60 * 24));
      if (diffDays === 0)
        return "Today";
      if (diffDays === 1)
        return "Yesterday";
      if (diffDays < 7)
        return `${diffDays} days ago`;
      return timestamp.toLocaleDateString();
    };
    const formatTimestamp = () => {
      const timestamp = new Date(props.post.timestamp);
      return timestamp.toLocaleString();
    };
    onMounted(() => {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              observer.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: "50px",
          threshold: 0.1
        }
      );
      if (postRef.value) {
        observer.observe(postRef.value);
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<article${ssrRenderAttrs(mergeProps({
        class: "post-card",
        ref_key: "postRef",
        ref: postRef
      }, _attrs))} data-v-cdf3720c>`);
      if (hasMediaContent.value) {
        _push(`<div class="media-container" data-v-cdf3720c>`);
        if (showImage.value) {
          _push(`<img${ssrRenderAttr("src", __props.post.media_url)}${ssrRenderAttr("alt", __props.post.text || "Post image")} class="post-image" loading="lazy" data-v-cdf3720c>`);
        } else {
          _push(`<!---->`);
        }
        if (showVideo.value) {
          _push(`<video controls preload="metadata" class="post-video" data-v-cdf3720c><source${ssrRenderAttr("src", __props.post.video_url)} type="video/mp4" data-v-cdf3720c> Your browser does not support the video tag. </video>`);
        } else {
          _push(`<!---->`);
        }
        if (!showImage.value && !showVideo.value) {
          _push(`<div class="media-placeholder" data-v-cdf3720c><span class="icon" data-v-cdf3720c>Media unavailable</span></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div>`);
      } else {
        _push(`<div class="media-placeholder" data-v-cdf3720c><span class="icon" data-v-cdf3720c>Text post</span></div>`);
      }
      _push(`<div class="content-section" data-v-cdf3720c>`);
      if (__props.post.text) {
        _push(`<p class="${ssrRenderClass([{ "has-media": hasMediaContent.value }, "post-text"])}" data-v-cdf3720c>${ssrInterpolate(__props.post.text)}</p>`);
      } else {
        _push(`<!---->`);
      }
      if (__props.post.tags && __props.post.tags.length > 0) {
        _push(`<div class="tags-section" data-v-cdf3720c><!--[-->`);
        ssrRenderList(__props.post.tags, (tag) => {
          _push(`<span class="tag" tabindex="0" role="button" data-v-cdf3720c>${ssrInterpolate(tag)}</span>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="metadata-section" data-v-cdf3720c><span class="author" data-v-cdf3720c>${ssrInterpolate(__props.post.author)}</span><span class="timestamp"${ssrRenderAttr("title", formatTimestamp())} data-v-cdf3720c>${ssrInterpolate(formatRelativeTime())}</span></div></div><div class="engagement-section" data-v-cdf3720c><div class="metrics-placeholder" data-v-cdf3720c><span class="info-text" data-v-cdf3720c>View post details for more info</span></div></div>`);
      if (__props.loading) {
        _push(`<div class="loading-spinner" data-v-cdf3720c>Loading...</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</article>`);
    };
  }
};
const _sfc_setup$4 = _sfc_main$4.setup;
_sfc_main$4.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/features/short-form/components/PostCard.vue");
  return _sfc_setup$4 ? _sfc_setup$4(props, ctx) : void 0;
};
const PostCard = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-cdf3720c"]]);
const PostModal_vue_vue_type_style_index_0_scoped_9e39a4c1_lang = "";
const _sfc_main$3 = {
  __name: "PostModal",
  __ssrInlineRender: true,
  props: {
    post: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ["close"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const isVisible = ref(true);
    ref(null);
    const imageFailed = ref(false);
    const videoFailed = ref(false);
    const showImage = computed(() => Boolean(props.post.media_url) && !imageFailed.value);
    const showVideo = computed(() => Boolean(props.post.video_url) && !videoFailed.value);
    const formatRelativeTime = () => {
      const timestamp = new Date(props.post.timestamp);
      const now = /* @__PURE__ */ new Date();
      const diffMs = now - timestamp;
      const diffDays = Math.floor(diffMs / (1e3 * 60 * 60 * 24));
      if (diffDays === 0)
        return "Today";
      if (diffDays === 1)
        return "Yesterday";
      if (diffDays < 7)
        return `${diffDays} days ago`;
      return timestamp.toLocaleDateString();
    };
    const formatTimestamp = () => {
      const timestamp = new Date(props.post.timestamp);
      return timestamp.toLocaleString();
    };
    onMounted(() => {
      document.body.style.overflow = "hidden";
    });
    onUnmounted(() => {
      document.body.style.overflow = "";
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<!--[--><div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title" style="${ssrRenderStyle(isVisible.value ? null : { display: "none" })}" data-v-9e39a4c1><div class="modal-content" data-v-9e39a4c1><button class="close-button" aria-label="Close modal" data-v-9e39a4c1> x </button><header class="modal-header" data-v-9e39a4c1><h2 id="modal-title" class="modal-title" data-v-9e39a4c1>Post Details</h2></header><div class="modal-body" data-v-9e39a4c1>`);
      if (__props.post.media_url || __props.post.video_url) {
        _push(`<div class="media-section" data-v-9e39a4c1>`);
        if (showImage.value) {
          _push(`<img${ssrRenderAttr("src", __props.post.media_url)}${ssrRenderAttr("alt", __props.post.text || "Post image")} class="modal-image" loading="lazy" data-v-9e39a4c1>`);
        } else {
          _push(`<!---->`);
        }
        if (showVideo.value) {
          _push(`<video controls preload="metadata" class="modal-video" data-v-9e39a4c1><source${ssrRenderAttr("src", __props.post.video_url)} type="video/mp4" data-v-9e39a4c1> Your browser does not support the video tag. </video>`);
        } else {
          _push(`<!---->`);
        }
        if (!showImage.value && !showVideo.value) {
          _push(`<div class="media-placeholder" data-v-9e39a4c1><span class="icon" data-v-9e39a4c1>Media unavailable</span></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="content-section" data-v-9e39a4c1>`);
      if (__props.post.text) {
        _push(`<section class="post-text-section" data-v-9e39a4c1><h3 class="post-caption" data-v-9e39a4c1>Caption</h3><p class="post-text" data-v-9e39a4c1>${ssrInterpolate(__props.post.text)}</p></section>`);
      } else {
        _push(`<!---->`);
      }
      if (__props.post.tags && __props.post.tags.length > 0) {
        _push(`<section class="tags-section" data-v-9e39a4c1><h3 class="section-title" data-v-9e39a4c1>Tags</h3><div class="tags-container" data-v-9e39a4c1><!--[-->`);
        ssrRenderList(__props.post.tags, (tag) => {
          _push(`<span class="tag" data-v-9e39a4c1>${ssrInterpolate(tag)}</span>`);
        });
        _push(`<!--]--></div></section>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<section class="metadata-section" data-v-9e39a4c1><h3 class="section-title" data-v-9e39a4c1>Metadata</h3><div class="metadata-grid" data-v-9e39a4c1><div class="metadata-item" data-v-9e39a4c1><span class="label" data-v-9e39a4c1>Author:</span><span class="value" data-v-9e39a4c1>${ssrInterpolate(__props.post.author)}</span></div><div class="metadata-item" data-v-9e39a4c1><span class="label" data-v-9e39a4c1>Posted:</span><span class="value"${ssrRenderAttr("title", formatTimestamp())} data-v-9e39a4c1>${ssrInterpolate(formatRelativeTime())}</span></div><div class="metadata-item" data-v-9e39a4c1><span class="label" data-v-9e39a4c1>Post ID:</span><span class="value" data-v-9e39a4c1>${ssrInterpolate(__props.post.id)}</span></div></div></section></div></div><footer class="modal-footer" data-v-9e39a4c1><button class="close-btn" aria-label="Close and return to feed" data-v-9e39a4c1> Close </button></footer></div></div>`);
      if (__props.loading) {
        _push(`<div class="modal-loading" data-v-9e39a4c1><div class="spinner" data-v-9e39a4c1></div><span data-v-9e39a4c1>Loading post details...</span></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<!--]-->`);
    };
  }
};
const _sfc_setup$3 = _sfc_main$3.setup;
_sfc_main$3.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/features/short-form/components/PostModal.vue");
  return _sfc_setup$3 ? _sfc_setup$3(props, ctx) : void 0;
};
const PostModal = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-9e39a4c1"]]);
const SearchBar_vue_vue_type_style_index_0_scoped_33b8cef8_lang = "";
const _sfc_main$2 = {
  __name: "SearchBar",
  __ssrInlineRender: true,
  props: {
    modelValue: {
      type: String,
      default: ""
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ["update:modelValue", "search"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const keyword = ref(props.modelValue);
    ref(null);
    ref(null);
    const hasKeyword = computed(() => keyword.value.trim().length > 0);
    watch(
      () => props.modelValue,
      (value) => {
        if (value !== keyword.value) {
          keyword.value = value || "";
        }
      }
    );
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "search-bar-container" }, _attrs))} data-v-33b8cef8><input type="text"${ssrRenderAttr("value", keyword.value)} placeholder="Search posts..."${ssrIncludeBooleanAttr(__props.loading) ? " disabled" : ""} class="search-input" aria-label="Search posts by keyword" data-v-33b8cef8>`);
      if (hasKeyword.value && !__props.loading) {
        _push(`<button class="clear-button" aria-label="Clear search" data-v-33b8cef8> x </button>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/features/short-form/components/SearchBar.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const SearchBar = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-33b8cef8"]]);
const TagFilter_vue_vue_type_style_index_0_scoped_e047c887_lang = "";
const _sfc_main$1 = {
  __name: "TagFilter",
  __ssrInlineRender: true,
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    availableTags: {
      type: Array,
      default: () => []
    }
  },
  emits: ["update:modelValue", "change"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const selectedTags = ref([...props.modelValue]);
    const filterText = ref("");
    const isOpen = ref(false);
    const currentIndex = ref(-1);
    const id = `tag-filter-${Math.random().toString(36).slice(2, 9)}`;
    const containerRef = ref(null);
    watch(
      () => props.modelValue,
      (newVal) => {
        selectedTags.value = [...newVal || []];
      }
    );
    const filteredOptions = computed(() => {
      const searchTerm = filterText.value.toLowerCase().trim();
      return (props.availableTags || []).map((tag) => ({ value: tag, label: tag })).filter((option) => !searchTerm || option.label.toLowerCase().includes(searchTerm));
    });
    const isSelected = (tag) => selectedTags.value.includes(tag);
    const closeDropdown = () => {
      isOpen.value = false;
      filterText.value = "";
      currentIndex.value = -1;
    };
    const handleDocumentClick = (event) => {
      if (!containerRef.value)
        return;
      if (!containerRef.value.contains(event.target)) {
        closeDropdown();
      }
    };
    onMounted(() => {
      document.addEventListener("click", handleDocumentClick);
    });
    onUnmounted(() => {
      document.removeEventListener("click", handleDocumentClick);
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: "tag-filter-container",
        ref_key: "containerRef",
        ref: containerRef
      }, _attrs))} data-v-e047c887><label class="tag-label" for="tag-filter" data-v-e047c887>Filter by tags:</label>`);
      if (selectedTags.value.length > 0) {
        _push(`<div class="selected-tags" data-v-e047c887><!--[-->`);
        ssrRenderList(selectedTags.value, (tag) => {
          _push(`<span class="tag-pill" tabindex="0" role="button" data-v-e047c887>${ssrInterpolate(tag)} <span class="remove-icon" data-v-e047c887>x</span></span>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="dropdown-container" data-v-e047c887><input id="tag-filter" type="text"${ssrRenderAttr("value", filterText.value)} placeholder="Select tags..." class="filter-input"${ssrRenderAttr("aria-expanded", isOpen.value)}${ssrRenderAttr("aria-controls", `tag-options-${id}`)} data-v-e047c887><div class="dropdown-menu"${ssrRenderAttr("id", `tag-options-${id}`)} style="${ssrRenderStyle(isOpen.value ? null : { display: "none" })}" data-v-e047c887><!--[-->`);
      ssrRenderList(filteredOptions.value, (option, index) => {
        _push(`<div class="${ssrRenderClass([{ selected: isSelected(option.value), active: index === currentIndex.value }, "dropdown-option"])}" tabindex="-1" data-v-e047c887><span class="tag-checkbox" data-v-e047c887><input type="checkbox"${ssrIncludeBooleanAttr(isSelected(option.value)) ? " checked" : ""} readonly data-v-e047c887></span><span class="tag-label-display" data-v-e047c887>${ssrInterpolate(option.label)}</span></div>`);
      });
      _push(`<!--]-->`);
      if (filteredOptions.value.length === 0) {
        _push(`<div class="no-results" data-v-e047c887>No matching tags found</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div></div>`);
    };
  }
};
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/features/short-form/components/TagFilter.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const TagFilter = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-e047c887"]]);
const API_BASE = "/api/short-form";
const LEGACY_API_BASE = "/api";
const feedService = {
  async getFeed(params = {}) {
    var _a;
    const { page = 1, limit = 20, tags = [], keyword = "" } = params;
    const queryParams = new URLSearchParams({
      page: String(page),
      limit: String(limit)
    });
    if (Array.isArray(tags) && tags.length > 0) {
      tags.forEach((tag) => queryParams.append("tags", tag));
    }
    if (keyword && keyword.trim()) {
      queryParams.append("keyword", keyword.trim());
    }
    try {
      const response = await axios.get(`${API_BASE}/feed?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      if (((_a = error == null ? void 0 : error.response) == null ? void 0 : _a.status) !== 404) {
        throw error;
      }
      const legacyResponse = await axios.get(
        `${LEGACY_API_BASE}/feed?${queryParams.toString()}`
      );
      return legacyResponse.data;
    }
  },
  async getPost(postId) {
    var _a;
    try {
      const response = await axios.get(`${API_BASE}/posts/${postId}`);
      return response.data.post;
    } catch (error) {
      if (((_a = error == null ? void 0 : error.response) == null ? void 0 : _a.status) !== 404) {
        throw error;
      }
      const legacyResponse = await axios.get(`${LEGACY_API_BASE}/post/${postId}`);
      return legacyResponse.data.post;
    }
  }
};
const ShortFormFeedPage_vue_vue_type_style_index_0_scoped_b97b305e_lang = "";
const postsPerPage = 20;
const _sfc_main = {
  __name: "ShortFormFeedPage",
  __ssrInlineRender: true,
  setup(__props) {
    const posts = ref([]);
    const selectedTags = ref([]);
    const searchKeyword = ref("");
    const loading = ref(false);
    const isLoadingData = ref(false);
    const selectedPost = ref(null);
    const loadTrigger = ref(null);
    const currentPage = ref(1);
    const totalPages = ref(0);
    const allTags = ref([]);
    let feedObserver = null;
    const hasFilters = computed(() => selectedTags.value.length > 0 || searchKeyword.value.trim() !== "");
    const hasMorePages = computed(() => currentPage.value < totalPages.value);
    const getResultCount = (response) => {
      var _a, _b;
      return ((_a = response == null ? void 0 : response.pagination) == null ? void 0 : _a.total_posts) ?? ((_b = response == null ? void 0 : response.posts) == null ? void 0 : _b.length) ?? 0;
    };
    const emitAnalytics = (context, response) => {
      if (!(context == null ? void 0 : context.type)) {
        return;
      }
      const resultCount = getResultCount(response);
      if (context.type === "search") {
        trackEvent("shorts_search", {
          result_count: resultCount,
          keyword_length: context.keywordLength ?? 0
        });
        return;
      }
      if (context.type === "filter") {
        trackEvent("shorts_filter_apply", {
          result_count: resultCount,
          tag_count: selectedTags.value.length,
          tags: [...selectedTags.value]
        });
      }
    };
    const hydrateAvailableTags = async () => {
      try {
        const response = await feedService.getFeed({
          page: 1,
          limit: 100,
          tags: [],
          keyword: ""
        });
        if (Array.isArray(response.available_tags) && response.available_tags.length > 0) {
          allTags.value = response.available_tags;
          return;
        }
        const tagSet = /* @__PURE__ */ new Set();
        (response.posts || []).forEach((post) => {
          ;
          (post.tags || []).forEach((tag) => tagSet.add(tag));
        });
        allTags.value = Array.from(tagSet);
      } catch (error) {
        console.error("Failed to hydrate available tags:", error);
      }
    };
    const loadPosts = async (page = 1, reset = false, analyticsContext = null) => {
      var _a;
      if (loading.value || isLoadingData.value)
        return;
      loading.value = true;
      isLoadingData.value = true;
      try {
        const response = await feedService.getFeed({
          page,
          limit: postsPerPage,
          tags: selectedTags.value,
          keyword: searchKeyword.value.trim()
        });
        if (reset) {
          posts.value = response.posts || [];
          currentPage.value = 1;
        } else {
          posts.value = [...posts.value, ...response.posts || []];
          currentPage.value = page;
        }
        totalPages.value = ((_a = response.pagination) == null ? void 0 : _a.total_pages) || 0;
        if (allTags.value.length === 0) {
          if (Array.isArray(response.available_tags) && response.available_tags.length > 0) {
            allTags.value = response.available_tags;
          } else {
            const tagSet = /* @__PURE__ */ new Set();
            posts.value.forEach((post) => (post.tags || []).forEach((tag) => tagSet.add(tag)));
            allTags.value = Array.from(tagSet);
          }
        }
        emitAnalytics(analyticsContext, response);
      } catch (error) {
        console.error("Failed to load posts:", error);
      } finally {
        loading.value = false;
        isLoadingData.value = false;
      }
    };
    const handleFilterChange = () => {
      currentPage.value = 1;
      loadPosts(1, true, { type: "filter" });
    };
    const handleSearch = (keyword) => {
      searchKeyword.value = keyword;
      currentPage.value = 1;
      loadPosts(1, true, {
        type: "search",
        keywordLength: keyword.trim().length
      });
    };
    const handleFilterTag = (tag) => {
      if (!selectedTags.value.includes(tag)) {
        selectedTags.value = [...selectedTags.value, tag];
        handleFilterChange();
      }
    };
    const openDetailModal = (post) => {
      selectedPost.value = post;
    };
    const closeDetailModal = () => {
      selectedPost.value = null;
    };
    const setupObserver = () => {
      if (feedObserver) {
        feedObserver.disconnect();
      }
      feedObserver = new IntersectionObserver((entries) => {
        const [entry] = entries;
        if (!(entry == null ? void 0 : entry.isIntersecting))
          return;
        if (!hasMorePages.value || loading.value)
          return;
        loadPosts(currentPage.value + 1);
      }, { root: null, threshold: 0.1 });
      if (loadTrigger.value) {
        feedObserver.observe(loadTrigger.value);
      }
    };
    onMounted(async () => {
      await hydrateAvailableTags();
      await loadPosts(1);
      setupObserver();
    });
    watch(loadTrigger, () => {
      setupObserver();
    });
    onUnmounted(() => {
      if (feedObserver) {
        feedObserver.disconnect();
      }
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "feed-container" }, _attrs))} data-v-b97b305e><aside class="filters-sidebar" data-v-b97b305e><h2 class="filters-title" data-v-b97b305e>Filters</h2>`);
      _push(ssrRenderComponent(TagFilter, {
        modelValue: selectedTags.value,
        "onUpdate:modelValue": ($event) => selectedTags.value = $event,
        "available-tags": allTags.value,
        onChange: handleFilterChange,
        class: "filter-section"
      }, null, _parent));
      _push(ssrRenderComponent(SearchBar, {
        modelValue: searchKeyword.value,
        "onUpdate:modelValue": ($event) => searchKeyword.value = $event,
        onSearch: handleSearch,
        class: "filter-section"
      }, null, _parent));
      if (hasFilters.value) {
        _push(`<button class="clear-filters-btn" data-v-b97b305e> Clear All Filters </button>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</aside><main class="feed-main" data-v-b97b305e><h1 class="feed-title" data-v-b97b305e>Short-Form Content Feed</h1>`);
      if (loading.value && posts.value.length === 0) {
        _push(`<div class="loading-state" data-v-b97b305e><div class="spinner" data-v-b97b305e></div><p data-v-b97b305e>Loading posts...</p></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="posts-container" style="${ssrRenderStyle(!loading.value || posts.value.length > 0 ? null : { display: "none" })}" data-v-b97b305e><!--[-->`);
      ssrRenderList(posts.value, (post) => {
        _push(ssrRenderComponent(PostCard, {
          key: post.id,
          post,
          loading: loading.value,
          onClick: ($event) => openDetailModal(post),
          onFilterTag: handleFilterTag,
          class: "post-item"
        }, null, _parent));
      });
      _push(`<!--]-->`);
      if (hasMorePages.value && !loading.value) {
        _push(`<div class="load-trigger" data-v-b97b305e></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
      if (!loading.value && posts.value.length === 0 && !isLoadingData.value) {
        _push(`<div class="empty-state" data-v-b97b305e><h2 data-v-b97b305e>No posts available yet</h2><p data-v-b97b305e>Check back soon for new short-form content!</p></div>`);
      } else {
        _push(`<!---->`);
      }
      if (loading.value && posts.value.length > 0) {
        _push(`<div class="load-more-spinner" data-v-b97b305e><div class="spinner" data-v-b97b305e></div><span data-v-b97b305e>Loading more...</span></div>`);
      } else {
        _push(`<!---->`);
      }
      if (!hasMorePages.value && !loading.value && posts.value.length > 0) {
        _push(`<div class="no-more-posts" data-v-b97b305e><span data-v-b97b305e>All posts loaded</span></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</main>`);
      if (selectedPost.value) {
        _push(ssrRenderComponent(PostModal, {
          post: selectedPost.value,
          onClose: closeDetailModal
        }, null, _parent));
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
};
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/features/short-form/pages/ShortFormFeedPage.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const ShortFormFeedPage = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-b97b305e"]]);
const homeDescription = "Discover Quortol essays, podcasts, short-form posts, and interactive data storytelling.";
const blogDescription = "Read Quortol essays on technology, work, policy, and social futures.";
const podcastDescription = "Listen to Quortol podcast episodes adapted from essays and original conversations.";
const dataStorytellingDescription = "Interactive data storytelling dashboards and visual deep dives.";
const routes = [
  {
    path: "/",
    redirect: "/blog"
  },
  {
    path: "/blogs",
    redirect: "/blog"
  },
  {
    path: "/quortol-home",
    name: "home",
    component: Home,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Quortol Home",
        description: homeDescription,
        path: "/quortol-home",
        structuredData: [
          buildWebPageStructuredData({
            title: "Quortol Home",
            description: homeDescription,
            path: "/quortol-home"
          })
        ]
      })
    }
  },
  {
    path: "/blog",
    name: "blog",
    component: BlogList,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Quortol Blog",
        description: blogDescription,
        path: "/blog",
        structuredData: [
          buildCollectionPageStructuredData({
            title: "Quortol Blog",
            description: blogDescription,
            path: "/blog"
          })
        ]
      })
    }
  },
  {
    path: "/blog/:slug",
    name: "blog-detail",
    component: BlogDetail,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Quortol Blog",
        description: "Read longform essays from Quortol.",
        path: "/blog",
        ogType: "article"
      })
    }
  },
  {
    path: "/podcasts",
    name: "podcast-list",
    component: PodcastList,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Podcasts | Quortol",
        description: podcastDescription,
        path: "/podcasts",
        structuredData: [
          buildPodcastSeriesStructuredData({
            title: "Quortol Podcast",
            description: podcastDescription,
            path: "/podcasts"
          })
        ]
      })
    }
  },
  {
    path: "/podcasts/:slug",
    name: "podcast-detail",
    component: PodcastDetail,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Podcast Episode | Quortol",
        description: "Listen to a Quortol podcast episode.",
        path: "/podcasts",
        ogType: "article"
      })
    }
  },
  {
    path: "/agent/login",
    name: "agent-login",
    component: _sfc_main$7,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Agent Login | Quortol",
        description: "Sign in to the Quortol agent workspace.",
        path: "/agent/login",
        robots: "noindex,nofollow"
      })
    }
  },
  {
    path: "/agent/dashboard",
    name: "agent-dashboard",
    component: _sfc_main$6,
    meta: {
      requiresAuth: true,
      seo: buildStaticPageSEOPayload({
        title: "Agent Dashboard | Quortol",
        description: "Private dashboard for Quortol agent operations.",
        path: "/agent/dashboard",
        robots: "noindex,nofollow"
      })
    }
  },
  {
    path: "/agent/agents/:agentId/capabilities",
    name: "agent-capabilities",
    component: _sfc_main$5,
    meta: {
      requiresAuth: true,
      seo: buildStaticPageSEOPayload({
        title: "Agent Capabilities | Quortol",
        description: "Private capability configuration for Quortol agents.",
        path: "/agent/agents",
        robots: "noindex,nofollow"
      })
    }
  },
  {
    path: "/data-storytelling",
    name: "data-storytelling",
    component: () => import("./assets/DataStorytelling-7074c981.js"),
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Data Storytelling | Quortol",
        description: dataStorytellingDescription,
        path: "/data-storytelling",
        structuredData: [
          buildWebPageStructuredData({
            title: "Data Storytelling | Quortol",
            description: dataStorytellingDescription,
            path: "/data-storytelling"
          })
        ]
      })
    }
  },
  {
    path: "/data-storytelling/:dashboard",
    name: "dashboard-view",
    component: () => import("./assets/DataStorytellingDetail-b85c2dbf.js"),
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Dashboard View | Quortol",
        description: "Interactive dashboard detail view on Quortol.",
        path: "/data-storytelling",
        robots: "noindex,follow"
      })
    }
  },
  {
    path: "/shorts",
    name: "short-form-feed",
    component: ShortFormFeedPage,
    meta: {
      requiresAuth: false,
      seo: buildStaticPageSEOPayload({
        title: "Short-Form Content Feed | Quortol",
        description: "Browse short-form content posts with images, videos, and tags.",
        path: "/shorts",
        robots: "noindex,follow"
      })
    }
  }
];
const createAppRouter = (history = createWebHistory()) => {
  const router = createRouter({
    history,
    routes
  });
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    if (to.meta.requiresAuth) {
      if (!authStore.isAuthenticated) {
        next({ name: "agent-login", query: { redirect: to.fullPath } });
        return;
      }
    }
    next();
  });
  router.afterEach((to) => {
    var _a;
    if (typeof document === "undefined") {
      return;
    }
    const routeSEO = ((_a = to.meta) == null ? void 0 : _a.seo) || {};
    applySEOMetadata({
      title: routeSEO.title || "Quortol",
      description: routeSEO.description || "Quortol publishes essays, podcasts, short-form posts, and data storytelling projects.",
      robots: routeSEO.robots || "index,follow",
      path: to.path,
      canonical: routeSEO.canonical,
      ogType: routeSEO.ogType,
      ogImage: routeSEO.ogImage,
      twitterCard: routeSEO.twitterCard,
      structuredData: routeSEO.structuredData || []
    });
    if (isPublicAnalyticsPath(to.path)) {
      trackPageview();
    }
  });
  return router;
};
const bootstrap_min = "";
const createQuortolApp = ({ url = "/", ssr = false, prerenderPayload = null } = {}) => {
  const app = createSSRApp(_sfc_main$f);
  const pinia = createPinia();
  const history = ssr ? createMemoryHistory() : createWebHistory();
  const router = createAppRouter(history);
  const payload = prerenderPayload || (!ssr ? readClientPrerenderPayload() : null);
  app.use(pinia);
  app.use(router);
  app.provide(PRERENDER_CONTEXT_KEY, {
    path: (payload == null ? void 0 : payload.path) || url,
    routeData: (payload == null ? void 0 : payload.routeData) || null
  });
  return { app, router, pinia };
};
const render = async (url, manifestEntry) => {
  const { app, router } = createQuortolApp({
    url,
    ssr: true,
    prerenderPayload: {
      path: (manifestEntry == null ? void 0 : manifestEntry.path) || url,
      routeData: (manifestEntry == null ? void 0 : manifestEntry.pageData) || null
    }
  });
  await router.push(url);
  await router.isReady();
  const appHtml = await renderToString(app);
  return { appHtml };
};
export {
  _export_sfc as _,
  dataStorytelling as d,
  render,
  usePrerenderRouteData as u
};
