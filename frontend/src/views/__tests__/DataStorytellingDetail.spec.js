import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DataStorytellingDetail from '../DataStorytellingDetail.vue'

const { getDashboards, routeParams } = vi.hoisted(() => ({
  getDashboards: vi.fn(),
  routeParams: { dashboard: 'known' },
}))
vi.mock('../../services/api', () => ({ dataStorytelling: { getDashboards } }))
vi.mock('vue-router', () => ({ useRoute: () => ({ params: routeParams }) }))

describe('DataStorytellingDetail', () => {
  beforeEach(() => { getDashboards.mockReset(); routeParams.dashboard = 'known' })

  it('embeds only the path returned by the registry API', async () => {
    getDashboards.mockResolvedValue({ data: { dashboards: [{ slug: 'known', title: 'Known', description: 'Story', embed_path: '/data-storytelling-app/known' }] } })
    const wrapper = mount(DataStorytellingDetail, { global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
    await flushPromises()
    expect(wrapper.find('iframe').attributes('src')).toBe('/data-storytelling-app/known')
  })

  it('shows a not-found state for an unregistered slug', async () => {
    routeParams.dashboard = 'unknown'
    getDashboards.mockResolvedValue({ data: { dashboards: [] } })
    const wrapper = mount(DataStorytellingDetail, { global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
    await flushPromises()
    expect(wrapper.text()).toContain('Dashboard not found')
    expect(wrapper.find('iframe').exists()).toBe(false)
  })
})
