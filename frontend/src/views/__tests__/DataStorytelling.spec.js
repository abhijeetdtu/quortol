import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { computed } from 'vue'
import DataStorytelling from '../DataStorytelling.vue'

const { getDashboards } = vi.hoisted(() => ({ getDashboards: vi.fn() }))
vi.mock('../../services/api', () => ({ dataStorytelling: { getDashboards } }))
vi.mock('../../prerender/context', () => ({ usePrerenderRouteData: () => computed(() => null) }))

const dashboards = [
  { slug: 'first', title: 'First', description: 'One', public_path: '/data-storytelling/first' },
  { slug: 'second', title: 'Second', description: 'Two', public_path: '/data-storytelling/second' },
]

describe('DataStorytelling', () => {
  beforeEach(() => getDashboards.mockReset())

  it('renders the registry response as featured and latest entries', async () => {
    getDashboards.mockResolvedValue({ data: { dashboards } })
    const wrapper = mount(DataStorytelling, { global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
    await flushPromises()
    expect(wrapper.text()).toContain('First')
    expect(wrapper.text()).toContain('Second')
    expect(wrapper.text()).toContain('Featured dashboard')
    wrapper.unmount()
  })

  it('renders the empty state', async () => {
    getDashboards.mockResolvedValue({ data: { dashboards: [] } })
    const wrapper = mount(DataStorytelling, { global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
    await flushPromises()
    expect(wrapper.text()).toContain('No dashboards are available yet')
  })
})
