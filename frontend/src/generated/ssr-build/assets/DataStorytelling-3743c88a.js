import { computed, mergeProps, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderAttr } from "vue/server-renderer";
import { useRoute } from "vue-router";
import { _ as _export_sfc } from "../entry-server.js";
import "@vue/server-renderer";
import "pinia";
import "axios";
import "markdown-it";
import "highlight.js";
const DataStorytelling_vue_vue_type_style_index_0_scoped_1c0e7fd8_lang = "";
const _sfc_main = {
  __name: "DataStorytelling",
  __ssrInlineRender: true,
  setup(__props) {
    const route = useRoute();
    const iframeSrc = computed(() => {
      const dashboard = typeof route.params.dashboard === "string" ? route.params.dashboard.trim() : "";
      return dashboard ? `/data-storytelling-app/${dashboard}` : "/data-storytelling-app/";
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({ class: "container-xl py-4" }, _attrs))} data-v-1c0e7fd8><header class="mb-3" data-v-1c0e7fd8><p class="kicker mb-2" data-v-1c0e7fd8>Data Storytelling</p><h1 class="h2 mb-2" data-v-1c0e7fd8>Interactive dashboards and visual deep dives</h1><p class="intro mb-0" data-v-1c0e7fd8> Explore Quortol dashboards in an embedded workspace built for exploratory analysis and longform visual explanation. </p></header><div class="card app-card" data-v-1c0e7fd8><div class="card-body p-0" data-v-1c0e7fd8><iframe${ssrRenderAttr("src", iframeSrc.value)} title="Data Storytelling" class="dashboard-frame" data-v-1c0e7fd8></iframe></div></div></section>`);
    };
  }
};
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("src/views/DataStorytelling.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const DataStorytelling = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-1c0e7fd8"]]);
export {
  DataStorytelling as default
};
